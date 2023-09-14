import os

from sqlalchemy import text
from phdi.linkage.mpi.postgres_mpi import PGMPIConnectorClient


def _init_db() -> PGMPIConnectorClient:
    os.environ = {
        "mpi_dbname": "testdb",
        "mpi_user": "postgres",
        "mpi_password": "pw",
        "mpi_host": "localhost",
        "mpi_port": "5432",
        "mpi_db_type": "postgres",
    }

    eng = PGMPIConnectorClient()

    # Generate test tables
    funcs = {
        "drop tables": (
            """
        DROP TABLE IF EXISTS patient;
        DROP TABLE IF EXISTS person;
        """
        ),
        "create_patient": (
            """CREATE EXTENSION IF NOT EXISTS "uuid-ossp";"""
            + "CREATE TABLE IF NOT EXISTS patient "
            + "(patient_id UUID DEFAULT uuid_generate_v4 (), person_id UUID, "
            + "zip VARCHAR(5), city VARCHAR(100));"
        ),
        "create_person": (
            """
            BEGIN;

            CREATE EXTENSION IF NOT EXISTS "uuid-ossp";"""
            + "CREATE TABLE IF NOT EXISTS person "
            + "(person_id UUID DEFAULT uuid_generate_v4 (), "
            + "external_person_id VARCHAR(100));"
        ),
    }

    for command, statement in funcs.items():
        try:
            with eng.dal.engine.connect() as db_conn:
                db_conn.execute(text(statement))
                db_conn.commit()
                print(f"{command} WORKED!")
        except Exception as e:
            print(f"{command} was unsuccessful")
            print(e)
            with eng.dal.engine.connect() as db_conn:
                db_conn.rollback()
    eng.initialize_schema()
    return eng


def test_block_data():
    PGDAL = _init_db()
    data_requested = {"zip": "90210", "city": "Los Angeles"}
    test_data = [data_requested]
    PGDAL.dal.bulk_insert(test_data)
    blocked_data = PGDAL.block_data(data_requested)
    print("HERE2:")
    print(blocked_data)
    assert 1 == 2
