import os
import pathlib
import re
import pytest

from sqlalchemy import Select, select, text
from phdi.linkage.postgres_mpi import PGMPIConnectorClient
from phdi.linkage.dal import DataAccessLayer
from sqlalchemy.orm import Session


def _init_db() -> DataAccessLayer:
    os.environ = {
        "mpi_dbname": "testdb",
        "mpi_user": "postgres",
        "mpi_password": "pw",
        "mpi_host": "localhost",
        "mpi_port": "5432",
        "mpi_db_type": "postgres",
    }
    MPI = PGMPIConnectorClient()
    MPI.dal.get_connection(
        engine_url="postgresql+psycopg2://postgres:pw@localhost:5432/testdb"
    )
    _clean_up(MPI.dal)

    # load ddl
    schema_ddl = open(
        pathlib.Path(__file__).parent.parent.parent
        / "phdi"
        / "linkage"
        / "new_tables.ddl"
    ).read()

    try:
        with MPI.dal.engine.connect() as db_conn:
            db_conn.execute(text(schema_ddl))
            db_conn.commit()
    except Exception as e:
        print(e)
        with MPI.dal.engine.connect() as db_conn:
            db_conn.rollback()
    MPI.dal.initialize_schema()
    return MPI


def _clean_up(dal):
    with dal.engine.connect() as pg_connection:
        pg_connection.execute(text("""DROP TABLE IF EXISTS external_person CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS external_source CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS address CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS phone_number CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS identifier CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS give_name CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS given_name CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS name CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS patient CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS person CASCADE;"""))
        pg_connection.commit()
        pg_connection.close()


def test_block_data():
    MPI = _init_db()
    block_data = {
        "dob": {"value": "1977-11-11"},
        "sex": {"value": "M"},
    }

    pt1 = {
        "person_id": None,
        "dob": "1977-11-11",
        "sex": "M",
        "race": "UNK",
        "ethnicity": "UNK",
    }
    pt2 = {
        "person_id": None,
        "dob": "1988-01-01",
        "sex": "F",
        "race": "UNK",
        "ethnicity": "UNK",
    }
    test_data = []
    test_data.append(pt1)
    test_data.append(pt2)
    MPI.dal.bulk_insert(MPI.dal.PATIENT_TABLE, test_data)
    blocked_data = MPI.block_data(block_data)

    _clean_up(MPI.dal)

    # ensure blocked data has two rows, headers and data
    assert len(blocked_data) == 2
    assert blocked_data[1][0] is not None
    assert blocked_data[0][0] == "patient_id"
    assert blocked_data[1][1] is None
    assert blocked_data[0][1] == "person_id"
    assert blocked_data[1][2].strftime("%Y-%m-%d") == "1977-11-11"
    assert blocked_data[0][2] == "dob"
    assert len(blocked_data[0]) == 13


def test_block_data_failures():
    MPI = _init_db()
    block_data = {}
    blocked_data = None
    # test empty block vals
    with pytest.raises(ValueError) as e:
        blocked_data = MPI.block_data(block_data)
        assert "`block_data` cannot be empty." in str(e.value)

    block_data = {
        "dob": {"value": "1977-11-11"},
        "sex": {"value": "M"},
        "MYADDR": {"value": "BLAH"},
    }

    pt1 = {
        "person_id": None,
        "dob": "1977-11-11",
        "sex": "M",
        "race": "UNK",
        "ethnicity": "UNK",
    }
    pt2 = {
        "person_id": None,
        "dob": "1988-01-01",
        "sex": "F",
        "race": "UNK",
        "ethnicity": "UNK",
    }
    test_data = []
    test_data.append(pt1)
    test_data.append(pt2)
    MPI.dal.bulk_insert(MPI.dal.PATIENT_TABLE, test_data)
    blocked_data = MPI.block_data(block_data)

    _clean_up(MPI.dal)

    # ensure blocked data has two rows, headers and data
    # testing to ensure that invalid block vals are skipped
    #  and not used in the filtering of the query
    assert len(blocked_data) == 2
    assert blocked_data[1][0] is not None
    assert blocked_data[0][0] == "patient_id"
    assert blocked_data[1][1] is None
    assert blocked_data[0][1] == "person_id"
    assert blocked_data[1][2].strftime("%Y-%m-%d") == "1977-11-11"
    assert blocked_data[0][2] == "dob"
    assert len(blocked_data[0]) == 13


def test_get_base_query():
    MPI: PGMPIConnectorClient = _init_db()
    base_query = MPI._get_base_query()
    assert base_query is not None
    assert isinstance(base_query, Select)
    _clean_up(MPI.dal)


def test_organize_block_criteria():
    MPI: PGMPIConnectorClient = _init_db()
    block_data = {
        "dob": {"value": "1977-11-11"},
        "sex": {"value": "M"},
        "MYADDR": {"value": "BLAH"},
    }

    expected_block_data = {
        "patient": {"criteria": {"dob": {"value": "1977-11-11"}, "sex": {"value": "M"}}}
    }
    expected_table = MPI.dal.PATIENT_TABLE

    result_block = MPI._organize_block_criteria(block_data)
    result_table = result_block["patient"]["table"]
    del result_block["patient"]["table"]
    assert expected_table == result_table
    assert result_block == expected_block_data

    block_data = {
        "dob": {"value": "1977-11-11"},
        "sex": {"value": "M"},
        "line_1": {"value": "BLAH"},
    }

    expected_block_data = {
        "patient": {
            "criteria": {"dob": {"value": "1977-11-11"}, "sex": {"value": "M"}}
        },
        "address": {"criteria": {"line_1": {"value": "BLAH"}}},
    }

    result_block = MPI._organize_block_criteria(block_data)
    result_table = result_block["address"]["table"]
    expected_table = MPI.dal.ADDRESS_TABLE
    del result_block["patient"]["table"]
    del result_block["address"]["table"]

    _clean_up(MPI.dal)
    assert expected_table == result_table
    assert result_block == expected_block_data


def test_generate_where_criteria():
    MPI = _init_db()
    block_data = {
        "dob": {"value": "1977-11-11"},
        "sex": {"value": "M"},
    }

    where_crit = MPI._generate_where_criteria(
        block_vals=block_data, table_name="patient"
    )
    expected_result = ["patient.dob = '1977-11-11'", "patient.sex = 'M'"]

    assert where_crit == expected_result


def test_generate_block_query():
    MPI = _init_db()
    block_data = {
        "patient": {
            "table": MPI.dal.PATIENT_TABLE,
            "criteria": {
                "dob": {"value": "1977-11-11"},
                "sex": {"value": "M"},
            },
        }
    }

    base_query = select(MPI.dal.PATIENT_TABLE)
    my_query = MPI._generate_block_query(block_data, base_query)

    expected_result = (
        "WITH patient_cte AS"
        + "(SELECT patient.patient_id AS patient_id"
        + "FROM patient"
        + "WHERE patient.dob = '1977-11-11' AND patient.sex = 'M')"
        + "SELECT patient.patient_id, patient.person_id, patient.dob,"
        + "patient.sex, patient.race, patient.ethnicity"
        + "FROM patient JOIN patient_cte ON "
        + "patient_cte.patient_id = patient.patient_id"
    )
    # ensure query has the proper where clause added
    assert re.sub(r"\s+", "", str(my_query)) == re.sub(r"\s+", "", expected_result)

    MPI = _init_db()
    block_data2 = {
        "given_name": {
            "table": MPI.dal.GIVEN_NAME_TABLE,
            "criteria": {"given_name": {"value": "Homer"}},
        },
        "name": {
            "table": MPI.dal.NAME_TABLE,
            "criteria": {"last_name": {"value": "Simpson"}},
        },
    }

    base_query2 = select(MPI.dal.PATIENT_TABLE)
    my_query2 = MPI._generate_block_query(block_data2, base_query2)

    _clean_up(MPI.dal)
    assert re.sub(r"\s+", "", str(my_query2)) == re.sub(r"\s+", "", expected_result)


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
    patient = {
        "person_id": None,
        "dob": "1977-11-11",
        "sex": "M",
        "race": "UNK",
        "ethnicity": "UNK",
    }
    result = eng.insert_match_patient(patient)
    assert result is None


def test_insert_person():
    eng = PGMPIConnectorClient()
    result = eng._insert_person(person_id="PID1", external_person_id="EXTPID2")
    assert result is None


# TODO: Update this test once we have transformations included
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
