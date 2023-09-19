import os
import pytest

from sqlalchemy import text
from phdi.linkage.postgres_mpi import PGMPIConnectorClient
from phdi.linkage.dal import DataAccessLayer
from sqlalchemy.orm import Session


def _init_db() -> PGMPIConnectorClient:
    os.environ = {
        "mpi_dbname": "testdb",
        "mpi_user": "postgres",
        "mpi_password": "pw",
        "mpi_host": "localhost",
        "mpi_port": "5432",
        "mpi_db_type": "postgres",
    }

    mpi = PGMPIConnectorClient()

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
            + "zip VARCHAR(5), city VARCHAR(100), PRIMARY KEY(patient_id));"
        ),
        "create_person": (
            """
            BEGIN;

            CREATE EXTENSION IF NOT EXISTS "uuid-ossp";"""
            + "CREATE TABLE IF NOT EXISTS person "
            + "(person_id UUID DEFAULT uuid_generate_v4 (), "
            + "external_person_id VARCHAR(100), PRIMARY KEY(person_id));"
        ),
    }

    for command, statement in funcs.items():
        try:
            with mpi.dal.engine.connect() as db_conn:
                db_conn.execute(text(statement))
                db_conn.commit()
                print(f"{command} WORKED!")
        except Exception as e:
            print(f"{command} was unsuccessful")
            print(e)
            with mpi.dal.engine.connect() as db_conn:
                db_conn.rollback()
    mpi._initialize_schema()
    return mpi


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
    MPI = _init_db()
    block_data = {"zip": {"value": "90210"}, "city": {"value": "Los Angeles"}}
    pt1 = {"zip": "83642", "city": "Meridian"}
    pt2 = {"zip": "90210", "city": "Los Angeles"}
    test_data = []
    test_data.append(pt1)
    test_data.append(pt2)
    MPI.dal.bulk_insert(MPI.dal.PATIENT_TABLE, test_data)
    blocked_data = MPI.block_data(block_data)

    _clean_up_postgres_client(MPI)

    # ensure blocked data has two rows, headers and data
    assert len(blocked_data) == 2
    assert blocked_data[1][1] is None
    assert blocked_data[1][2] == pt2.get("zip")


def test_block_data_failures():
    MPI = _init_db()
    block_data = {}
    blocked_data = None
    with pytest.raises(ValueError) as e:
        blocked_data = MPI.block_data(block_data)
        assert "`block_data` cannot be empty." in str(e.value)

    block_data = {
        "zip": {"value": "90210"},
        "city": {"value": "Los Angeles"},
        "MYADDR": {"value": "BLAH"},
    }
    data_requested = {"zip": "90210", "city": "Los Angeles"}
    test_data = []
    test_data.append(data_requested)
    MPI.dal.bulk_insert(MPI.dal.PATIENT_TABLE, test_data)
    blocked_data = MPI.block_data(block_data)

    _clean_up_postgres_client(MPI)

    # ensure blocked data has two rows, headers and data
    assert len(blocked_data) == 2
    assert blocked_data[1][1] is None
    assert blocked_data[1][2] == data_requested.get("zip")
    assert len(blocked_data[1]) == 4


def test_get_table_columns():
    MPI = _init_db()
    patient = MPI.dal.PATIENT_TABLE
    results = MPI._get_table_columns(patient)
    expected_result = ["patient_id", "person_id", "zip", "city"]
    assert results == expected_result


def test_generate_block_query():
    MPI = _init_db()
    block_data = {"zip": {"value": "90210"}, "city": {"value": "Los Angeles"}}
    db_conn = MPI.get_connection()
    expected_result = "patient.zip = '90210' AND patient.city = 'Los Angeles'"
    patient = MPI.dal.PATIENT_TABLE
    my_query = db_conn.query(patient)
    my_query = MPI._generate_block_query(block_data, my_query, patient)

    _clean_up_postgres_client(MPI)
    # ensure query has the proper where clause added
    assert str(my_query.whereclause) == expected_result


def test_pgmpi_connector():
    PDAL = _init_db()
    assert PDAL is not None
    session = PDAL.get_connection()
    assert session is not None


def test_init():
    os.environ = {
        "mpi_dbname": "testdb",
        "mpi_user": "postgres",
        "mpi_password": "pw",
        "mpi_host": "localhost",
        "mpi_port": "5432",
        "mpi_db_type": "postgres",
    }

    eng = PGMPIConnectorClient()

    assert eng is not None
    assert isinstance(eng, PGMPIConnectorClient)
    assert eng.dal is not None
    assert isinstance(eng.dal, DataAccessLayer)


def test_get_connection():
    os.environ = {
        "mpi_dbname": "testdb",
        "mpi_user": "postgres",
        "mpi_password": "pw",
        "mpi_host": "localhost",
        "mpi_port": "5432",
        "mpi_db_type": "postgres",
    }

    eng = PGMPIConnectorClient()
    db_conn = eng.get_connection()

    assert eng is not None
    assert isinstance(eng, PGMPIConnectorClient)
    assert eng.dal is not None
    assert isinstance(eng.dal, DataAccessLayer)
    assert db_conn is not None
    assert isinstance(db_conn, Session)


def test_insert_match_patient():
    eng = PGMPIConnectorClient()
    patient = {"zip": "90210", "city": "Los Angeles"}
    result = eng.insert_match_patient(patient)
    assert result is None


def test_insert_person():
    eng = PGMPIConnectorClient()
    result = eng._insert_person(person_id="PID1", external_person_id="EXTPID2")
    assert result is None


# def test_block_data_with_transform():
#     MPI = _init_db()
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
#     MPI.dal.bulk_insert(MPI.dal.PATIENT_TABLE, test_data)
#     blocked_data = MPI.block_data(data_requested)

#     _clean_up_postgres_client(MPI)

#     # ensure blocked data has two rows, headers and data
#     assert len(blocked_data) == 2
#     assert blocked_data[1][1] is None
#     assert blocked_data[1][2] == data_requested.get("zip")
