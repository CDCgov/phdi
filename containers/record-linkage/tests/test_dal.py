import datetime
import os
import pathlib

from app.linkage.dal import DataAccessLayer
from app.linkage.mpi import DIBBsMPIConnectorClient
from app.utils import _clean_up
from sqlalchemy import Engine
from sqlalchemy import select
from sqlalchemy import Table
from sqlalchemy import text


def _init_db() -> DataAccessLayer:
    dal = DataAccessLayer()
    dal.get_connection(
        engine_url="postgresql+psycopg2://postgres:pw@localhost:5432/testdb"
    )
    _clean_up(dal)

    # load ddl
    schema_ddl = open(
        pathlib.Path(__file__).parent.parent.parent.parent
        / "containers"
        / "record-linkage"
        / "migrations"
        / "V01_01__flat_schema.sql"
    ).read()

    try:
        with dal.engine.connect() as db_conn:
            db_conn.execute(text(schema_ddl))
            db_conn.commit()
    except Exception as e:
        print(e)
        with dal.engine.connect() as db_conn:
            db_conn.rollback()
    dal.initialize_schema()
    dal.get_session()
    return dal


def test_init_dal():
    dal = DataAccessLayer()

    assert dal.engine is None
    assert dal.PATIENT_TABLE is None
    assert dal.PERSON_TABLE is None


def test_get_connection():
    dal = DataAccessLayer()
    dal.get_connection(
        engine_url="postgresql+psycopg2://postgres:pw@localhost:5432/testdb"
    )

    assert dal.engine is not None
    assert isinstance(dal.engine, Engine)

    assert dal.PATIENT_TABLE is None
    assert dal.PERSON_TABLE is None
    assert dal.NAME_TABLE is None
    assert dal.GIVEN_NAME_TABLE is None
    assert dal.ID_TABLE is None
    assert dal.PHONE_TABLE is None
    assert dal.ADDRESS_TABLE is None
    assert dal.EXTERNAL_PERSON_TABLE is None
    assert dal.EXTERNAL_SOURCE_TABLE is None


def test_get_session():
    dal = DataAccessLayer()
    dal.get_connection(
        engine_url="postgresql+psycopg2://postgres:pw@localhost:5432/testdb"
    )
    dal.get_session()


def test_initialize_schema():
    dal = _init_db()

    assert dal.engine is not None
    assert isinstance(dal.engine, Engine)
    assert isinstance(dal.PATIENT_TABLE, Table)
    assert isinstance(dal.PERSON_TABLE, Table)
    assert isinstance(dal.NAME_TABLE, Table)
    assert isinstance(dal.GIVEN_NAME_TABLE, Table)
    assert isinstance(dal.ID_TABLE, Table)
    assert isinstance(dal.PHONE_TABLE, Table)
    assert isinstance(dal.ADDRESS_TABLE, Table)
    assert isinstance(dal.EXTERNAL_PERSON_TABLE, Table)
    assert isinstance(dal.EXTERNAL_SOURCE_TABLE, Table)


def test_bulk_insert_dict():
    dal = _init_db()

    data_requested = {
        "patient": [
            {
                "person_id": None,
                "dob": "1977-11-11",
                "sex": "male",
                "race": "UNK",
                "ethnicity": "UNK",
            },
        ],
    }
    insert_result = dal.bulk_insert_dict(data_requested, False)

    assert insert_result == {"patient": {"primary_keys": []}}

    results = dal.select_results(select(dal.PATIENT_TABLE))
    assert len(results) == 2
    assert results[1][2] == datetime.date(1977, 11, 11)
    assert results[1][3] == "male"
    assert results[1][0] is not None

    data_requested = {
        "person_id": None,
        "dob": "1988-01-01",
        "sex": "female",
        "race": "UNK",
        "ethnicity": "UNK",
        "MY ADDR": "BLAH",
    }
    data_req = []
    data_req.append(data_requested)
    error_msg = ""
    try:
        dal.bulk_insert_list(dal.PATIENT_TABLE, data_req, False)
    except Exception as error:
        error_msg = error
    finally:
        assert error_msg != ""
        session = dal.get_session()
        query = session.query(dal.PATIENT_TABLE)
        results = query.all()
        session.close()
        assert len(results) == 1
        assert results[0].dob == datetime.date(1977, 11, 11)
        assert results[0].sex == "male"
        assert results[0].patient_id is not None

    pt1 = {
        "person_id": None,
        "dob": "1985-11-11",
        "sex": "male",
        "race": "UNK",
        "ethnicity": "UNK",
    }
    pt2 = {
        "person_id": None,
        "dob": "1988-01-01",
        "sex": "female",
        "race": "UNK",
        "ethnicity": "UNK",
    }
    test_data2 = []
    test_data2.append(pt1)
    test_data2.append(pt2)
    data_requested2 = {
        "patient": test_data2,
    }
    pks = dal.bulk_insert_dict(data_requested2, True)
    assert len(pks.get("patient").get("primary_keys")) == 2
    results = dal.select_results(select(dal.PATIENT_TABLE))
    assert len(results) == 4

    _clean_up(dal)


def test_get_table_by_name():
    dal = _init_db()
    table = dal.get_table_by_name("patient")
    assert isinstance(table, Table)
    assert table.name == "patient"
    assert table.c is not None
    _clean_up(dal)

    dal2 = _init_db()

    table = dal2.get_table_by_name("address")
    assert isinstance(table, Table)
    assert table.name == "address"
    assert table.c is not None

    table = dal2.get_table_by_name(None)
    assert table is None

    table = dal2.get_table_by_name("customer")
    assert table is None
    _clean_up(dal2)


def test_get_table_by_column():
    dal = _init_db()
    table = dal.get_table_by_column("zip_code")
    assert table.name == "address"
    assert table.c is not None
    _clean_up(dal)

    dal2 = _init_db()
    dal2.initialize_schema()

    table = dal2.get_table_by_column("sex")
    assert table.name == "patient"
    assert table.c is not None

    table = dal2.get_table_by_column("")
    assert table is None

    table = dal2.get_table_by_column(None)
    assert table is None

    table = dal2.get_table_by_column("my_column")
    assert table is None

    _clean_up(dal2)


def test_does_table_have_column():
    dal = _init_db()
    assert dal.does_table_have_column(dal.GIVEN_NAME_TABLE, "patient_id") is False
    assert dal.does_table_have_column(dal.NAME_TABLE, "patient_id") is True
    assert dal.does_table_have_column(None, None) is False
    assert dal.does_table_have_column(dal.PATIENT_TABLE, None) is False
    assert dal.does_table_have_column(dal.PATIENT_TABLE, "") is False
    _clean_up(dal)


def test_select_results():
    os.environ = {
        "mpi_dbname": "testdb",
        "mpi_user": "postgres",
        "mpi_password": "pw",
        "mpi_host": "localhost",
        "mpi_port": "5432",
        "mpi_db_type": "postgres",
    }
    dal = _init_db()
    block_data = {
        "patient": {
            "table": dal.PATIENT_TABLE,
            "criteria": {
                "dob": {"value": "1977-11-11"},
                "sex": {"value": "male"},
            },
        }
    }

    pt1 = {
        "person_id": None,
        "dob": "1977-11-11",
        "sex": "male",
        "race": "UNK",
        "ethnicity": "UNK",
    }
    pt2 = {
        "person_id": None,
        "dob": "1988-01-01",
        "sex": "female",
        "race": "UNK",
        "ethnicity": "UNK",
    }
    records_to_add = [pt1, pt2]
    pks = dal.bulk_insert_list(dal.PATIENT_TABLE, records_to_add, True)
    mpi = DIBBsMPIConnectorClient()
    blocked_data_query = mpi._generate_block_query(
        block_data, select(dal.PATIENT_TABLE)
    )
    results = dal.select_results(select_statement=blocked_data_query)
    # ensure blocked data has two rows, headers and data
    assert len(results) == 2
    assert results[0][0] == "patient_id"
    assert results[1][0] == pks[0]
    assert results[1][0] != pks[1]
    assert results[0][2] == "dob"
    assert results[1][2] == datetime.date(1977, 11, 11)
    assert results[0][3] == "sex"
    assert results[1][3] == "male"

    results2 = dal.select_results(
        select_statement=blocked_data_query, include_col_header=False
    )

    # ensure blocked data has one row, just the data
    assert len(results2) == 1
    assert results2[0][0] == pks[0]
    assert results2[0][2] == datetime.date(1977, 11, 11)
    assert results2[0][3] == "male"

    _clean_up(dal)


def test_bulk_insert_list():
    dal = _init_db()
    pt1 = {
        "person_id": None,
        "dob": "1977-11-11",
        "sex": "male",
        "race": "UNK",
        "ethnicity": "Pacific Islander",
    }
    pt2 = {
        "person_id": "028b16d9-3055-40a8-a87f-f2bcf8c21a56",
        "dob": "1988-01-01",
        "sex": "female",
        "race": "White",
        "ethnicity": "UNK",
    }
    dal.bulk_insert_list(
        dal.PERSON_TABLE, [{"person_id": "028b16d9-3055-40a8-a87f-f2bcf8c21a56"}]
    )
    pat_data = [pt1, pt2]
    pk_list = dal.bulk_insert_list(dal.PATIENT_TABLE, pat_data, True)

    assert len(pk_list) == 2

    results = dal.select_results(select(dal.PATIENT_TABLE))
    assert len(results) == 3
    assert results[0][0] == "patient_id"
    assert results[1][0] == pk_list[0]
    assert results[2][0] == pk_list[1]
    assert results[0][3] == "sex"
    assert results[1][3] == pt1.get("sex")
    assert results[2][3] == pt2.get("sex")
    assert str(results[2][1]) == pt2.get("person_id")
    assert results[2][4] == pt2.get("race")
    assert results[1][5] == pt1.get("ethnicity")

    pat_data2 = [pt1, pt2]
    pk_list2 = dal.bulk_insert_list(dal.PATIENT_TABLE, pat_data2, False)
    assert len(pk_list2) == 0

    _clean_up(dal)
