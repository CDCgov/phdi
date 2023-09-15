from phdi.linkage.dal import PGDataAccessLayer
from sqlalchemy import Engine, Table, text
from sqlalchemy.orm import scoped_session


def test_init_dal():
    dal = PGDataAccessLayer()

    assert dal.engine is None
    assert dal.Session is None
    assert dal.PATIENT_TABLE is None
    assert dal.PERSON_TABLE is None


def test_get_connection():
    dal = PGDataAccessLayer()
    dal.get_connection(
        engine_url="postgresql+psycopg2://postgres:pw@localhost:5432/testdb"
    )

    assert dal.engine is not None
    assert isinstance(dal.engine, Engine)
    assert dal.Session is not None
    assert isinstance(dal.Session, scoped_session)
    assert dal.PATIENT_TABLE is None
    assert dal.PERSON_TABLE is None


def test_initialize_schema():
    dal = PGDataAccessLayer()
    dal.get_connection(
        engine_url="postgresql+psycopg2://postgres:pw@localhost:5432/testdb"
    )

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
            with dal.engine.connect() as db_conn:
                db_conn.execute(text(statement))
                db_conn.commit()
                print(f"{command} WORKED!")
        except Exception as e:
            print(f"{command} was unsuccessful")
            print(e)
            with dal.engine.connect() as db_conn:
                db_conn.rollback()
    dal.initialize_schema()

    assert dal.engine is not None
    assert isinstance(dal.engine, Engine)
    assert dal.Session is not None
    assert isinstance(dal.Session, scoped_session)
    assert dal.PATIENT_TABLE is not None
    assert isinstance(dal.PATIENT_TABLE, Table)
    assert dal.PERSON_TABLE is not None
    assert isinstance(dal.PERSON_TABLE, Table)


def test_bulk_insert_and_transactions():
    dal = PGDataAccessLayer()
    dal.get_connection(
        engine_url="postgresql+psycopg2://postgres:pw@localhost:5432/testdb"
    )

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
            with dal.engine.connect() as db_conn:
                db_conn.execute(text(statement))
                db_conn.commit()
                print(f"{command} WORKED!")
        except Exception as e:
            print(f"{command} was unsuccessful")
            print(e)
            with dal.engine.connect() as db_conn:
                db_conn.rollback()
    dal.initialize_schema()

    data_requested = {"zip": "90210", "city": "Los Angeles"}
    test_data = []
    test_data.append(data_requested)
    dal.bulk_insert(dal.PATIENT_TABLE, test_data)

    query = dal.Session.query(dal.PATIENT_TABLE)
    results = query.all()

    assert len(results) == 1
    assert results[0].zip == "90210"
    assert results[0].city == "Los Angeles"

    data_requested = {"MY ADDR": "BLAH", "zip": "90277", "city": "Bakerfield"}
    test_data = []
    error_msg = ""
    test_data.append(data_requested)
    try:
        dal.bulk_insert(dal.PATIENT_TABLE, test_data)
    except Exception as error:
        error_msg = error
    finally:
        assert error_msg != ""
        query = dal.Session.query(dal.PATIENT_TABLE)
        results = query.all()
        dal.Session.close()
        assert len(results) == 1
        assert results[0].zip == "90210"
        assert results[0].city == "Los Angeles"
