import os
from phdi.linkage.dal import PGDataAccessLayer
from sqlalchemy import Engine, Table, select, text
from sqlalchemy.orm import scoped_session
from phdi.linkage.postgres_mpi import PGMPIConnectorClient


def test_init_dal():
    dal = PGDataAccessLayer()

    assert dal.engine is None
    assert dal.session is None
    assert dal.PATIENT_TABLE is None
    assert dal.PERSON_TABLE is None


def test_get_connection():
    dal = PGDataAccessLayer()
    dal.get_connection(
        engine_url="postgresql+psycopg2://postgres:pw@localhost:5432/testdb"
    )

    assert dal.engine is not None
    assert isinstance(dal.engine, Engine)
    assert dal.session is not None
    assert isinstance(dal.session, scoped_session)
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
    assert dal.session is not None
    assert isinstance(dal.session, scoped_session)
    assert isinstance(dal.get_patient_table(), Table)
    assert isinstance(dal.get_person_table(), Table)


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

    query = dal.session.query(dal.PATIENT_TABLE)
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
        query = dal.session.query(dal.PATIENT_TABLE)
        results = query.all()
        dal.session.close()
        assert len(results) == 1
        assert results[0].zip == "90210"
        assert results[0].city == "Los Angeles"


def _init_db() -> PGDataAccessLayer:
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
    return dal


def _clean_up(dal):
    with dal.engine.connect() as pg_connection:
        pg_connection.execute(text("""DROP TABLE IF EXISTS patient;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS person;"""))
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
    block_data = {"zip": {"value": "90210"}, "city": {"value": "Los Angeles"}}
    pt1 = {"zip": "83642", "city": "Meridian"}
    pt2 = {"zip": "90210", "city": "Los Angeles"}
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
    assert results[1][1] is None
    assert results[1][2] == pt2.get("zip")
