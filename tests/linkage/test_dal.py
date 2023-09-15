from phdi.linkage.dal import PGDataAccessLayer
from sqlalchemy import text


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
    assert dal.Session is not None
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
    assert dal.Session is not None
    assert dal.PATIENT_TABLE is not None
    assert dal.PERSON_TABLE is not None


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
    dal.Session.close()

    assert dal.engine is not None
    assert dal.Session is not None
    assert dal.PATIENT_TABLE is not None
    assert dal.PERSON_TABLE is not None
    assert len(results) == 1
    assert results[0].zip == "90210"
    assert results[0].city == "Los Angeles"
