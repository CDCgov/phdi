import datetime
import os
import pathlib
from phdi.linkage.dal import DataAccessLayer
from sqlalchemy import Engine, Table, select, text
from sqlalchemy.orm import scoped_session
from phdi.linkage.postgres_mpi import PGMPIConnectorClient


def test_init_dal():
    dal = DataAccessLayer()

    assert dal.engine is None
    assert dal.session is None
    assert dal.PATIENT_TABLE is None
    assert dal.PERSON_TABLE is None


def test_get_connection():
    dal = DataAccessLayer()
    dal.get_connection(
        engine_url="postgresql+psycopg2://postgres:pw@localhost:5432/testdb"
    )

    assert dal.engine is not None
    assert isinstance(dal.engine, Engine)
    assert dal.session is not None
    assert isinstance(dal.session, scoped_session)
    assert dal.PATIENT_TABLE is None
    assert dal.PERSON_TABLE is None
    assert dal.NAME_TABLE is None
    assert dal.GIVEN_NAME_TABLE is None
    assert dal.ID_TABLE is None
    assert dal.PHONE_TABLE is None
    assert dal.ADDRESS_TABLE is None
    assert dal.EXT_PERSON_TABLE is None
    assert dal.EXT_SOURCE_TABLE is None


def test_initialize_schema():
    dal = _init_db()
    dal.initialize_schema()

    assert dal.engine is not None
    assert isinstance(dal.engine, Engine)
    assert dal.session is not None
    assert isinstance(dal.session, scoped_session)
    assert isinstance(dal.PATIENT_TABLE, Table)
    assert isinstance(dal.PERSON_TABLE, Table)
    assert isinstance(dal.NAME_TABLE, Table)
    assert isinstance(dal.GIVEN_NAME_TABLE, Table)
    assert isinstance(dal.ID_TABLE, Table)
    assert isinstance(dal.PHONE_TABLE, Table)
    assert isinstance(dal.ADDRESS_TABLE, Table)
    assert isinstance(dal.EXT_PERSON_TABLE, Table)
    assert isinstance(dal.EXT_SOURCE_TABLE, Table)


def test_bulk_insert_and_transactions():
    dal = _init_db()
    dal.initialize_schema()

    data_requested = {
        "person_id": None,
        "dob": "1977-11-11",
        "sex": "M",
        "race": "UNK",
        "ethnicity": "UNK",
    }
    test_data = []
    test_data.append(data_requested)
    dal.bulk_insert(dal.PATIENT_TABLE, test_data)

    query = dal.session.query(dal.PATIENT_TABLE)
    results = query.all()

    assert len(results) == 1
    assert results[0].dob == datetime.date(1977, 11, 11)
    assert results[0].sex == "M"
    assert results[0].patient_id is not None

    data_requested = {
        "person_id": None,
        "dob": "1988-01-01",
        "sex": "F",
        "race": "UNK",
        "ethnicity": "UNK",
        "MY ADDR": "BLAH",
    }
    test_data = []
    error_msg = ""
    test_data.append(data_requested)
    try:
        dal.bulk_insert(dal.PATIENT_TABLE, test_data)
    except Exception as error:
        error_msg = error
    finally:
        assert error_msg != ""
        query = dal.session.query(dal.PATIENT_TABLE)
        results = query.all()
        dal.session.close()
        assert len(results) == 1
        assert results[0].dob == datetime.date(1977, 11, 11)
        assert results[0].sex == "M"
        assert results[0].patient_id is not None

    _clean_up(dal)


def _init_db() -> DataAccessLayer:
    dal = DataAccessLayer()
    dal.get_connection(
        engine_url="postgresql+psycopg2://postgres:pw@localhost:5432/testdb"
    )
    _clean_up(dal)
    # load ddl
    schema_ddl = open(
        pathlib.Path(__file__).parent.parent.parent
        / "phdi"
        / "linkage"
        / "new_tables.ddl"
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
    return dal


def _clean_up(dal):
    with dal.engine.connect() as pg_connection:
        pg_connection.execute(text("""DROP TABLE IF EXISTS external_person CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS external_source CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS address CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS phone_number CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS identifier CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS given_name CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS name CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS patient CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS person CASCADE;"""))
        pg_connection.commit()
        pg_connection.close()


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
    dal.bulk_insert(dal.PATIENT_TABLE, test_data)
    mpi = PGMPIConnectorClient()
    blocked_data_query = mpi._generate_block_query(
        block_data, select(dal.PATIENT_TABLE), dal.PATIENT_TABLE
    )
    results = dal.select_results(select_stmt=blocked_data_query)

    _clean_up(dal)

    # ensure blocked data has two rows, headers and data
    assert len(results) == 2
    assert results[0][2] == "dob"
    assert results[1][2] == datetime.date(1977, 11, 11)
    assert results[0][3] == "sex"
    assert results[1][3] == "M"
