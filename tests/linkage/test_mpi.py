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
    eng._initialize_schema()
    return eng


def _clean_up_postgres_client(postgres_client):
    os.environ = {
        "mpi_dbname": "testdb",
        "mpi_user": "postgres",
        "mpi_password": "pw",
        "mpi_host": "localhost",
        "mpi_port": "5432",
        "mpi_db_type": "postgres",
    }

    with postgres_client.dal.engine.connect() as pg_connection:
        pg_connection.execute(text("""DROP TABLE IF EXISTS patient;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS person;"""))
        pg_connection.commit()
        pg_connection.close()


def test_block_data():
    PGDAL = _init_db()
    block_data = {"zip": {"value": "90210"}, "city": {"value": "Los Angeles"}}
    data_requested = {"zip": "90210", "city": "Los Angeles"}
    test_data = []
    test_data.append(data_requested)
    PGDAL.dal.bulk_insert(PGDAL.dal.PATIENT_TABLE, test_data)
    blocked_data = PGDAL.block_data(block_data)

    _clean_up_postgres_client(PGDAL)

    # ensure blocked data has two rows, headers and data
    assert len(blocked_data) == 2
    assert blocked_data[1][1] is None
    assert blocked_data[1][2] == data_requested.get("zip")


# def test_block_data_with_transform():
#     PGDAL = _init_db()
#     data_requested = {
#         "first_name": {"value": "John", "transformation": "first4"},
#         "last_name": {"value": "Shep", "transformation": "first4"},
#         "zip": {"value": "10001-0001"},
#         "city": {"value": "Faketon"},
#         "birthdate": {"value": "1983-02-01"},
#         "sex": {"value": "female"},
#         "state": {"value": "NY"},
#         "address": {"value": "e St", "transformation": "last4"},
#     }
#     test_data = []
#     test_data.append(data_requested)
#     PGDAL.dal.bulk_insert(PGDAL.dal.PATIENT_TABLE, test_data)
#     blocked_data = PGDAL.block_data(data_requested)

#     _clean_up_postgres_client(PGDAL)

#     # ensure blocked data has two rows, headers and data
#     assert len(blocked_data) == 2
#     assert blocked_data[1][1] is None
#     assert blocked_data[1][2] == data_requested.get("zip")
