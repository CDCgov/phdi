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


# def test_bulk_insert_and_transactions():
#     dal = _init_db()
#     dal.initialize_schema()

#     data_requested = {"zip": "90210", "city": "Los Angeles"}
#     test_data = []
#     test_data.append(data_requested)
#     dal.bulk_insert(dal.PATIENT_TABLE, test_data)

#     query = dal.session.query(dal.PATIENT_TABLE)
#     results = query.all()

#     assert len(results) == 1
#     assert results[0].zip == "90210"
#     assert results[0].city == "Los Angeles"

#     data_requested = {"MY ADDR": "BLAH", "zip": "90277", "city": "Bakerfield"}
#     test_data = []
#     error_msg = ""
#     test_data.append(data_requested)
#     try:
#         dal.bulk_insert(dal.PATIENT_TABLE, test_data)
#     except Exception as error:
#         error_msg = error
#     finally:
#         assert error_msg != ""
#         query = dal.session.query(dal.PATIENT_TABLE)
#         results = query.all()
#         dal.session.close()
#         assert len(results) == 1
#         assert results[0].zip == "90210"
#         assert results[0].city == "Los Angeles"


def _init_db() -> DataAccessLayer:
    dal = DataAccessLayer()
    dal.get_connection(
        engine_url="postgresql+psycopg2://postgres:pw@localhost:5432/testdb"
    )
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
        pg_connection.execute(text("""DROP TABLE IF EXISTS external_person;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS external_source;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS address;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS phone_number;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS identifier;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS given_name;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS name;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS patient;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS person;"""))
        pg_connection.commit()
        pg_connection.close()


# def test_select_results():
#     os.environ = {
#         "mpi_dbname": "testdb",
#         "mpi_user": "postgres",
#         "mpi_password": "pw",
#         "mpi_host": "localhost",
#         "mpi_port": "5432",
#         "mpi_db_type": "postgres",
#     }
#     dal = _init_db()
#     block_data = {"zip": {"value": "90210"}, "city": {"value": "Los Angeles"}}
#     pt1 = {"zip": "83642", "city": "Meridian"}
#     pt2 = {"zip": "90210", "city": "Los Angeles"}
#     test_data = []
#     test_data.append(pt1)
#     test_data.append(pt2)
#     dal.bulk_insert(dal.PATIENT_TABLE, test_data)
#     mpi = PGMPIConnectorClient()
#     blocked_data_query = mpi._generate_block_query(
#         block_data, select(dal.PATIENT_TABLE), dal.PATIENT_TABLE
#     )
#     results = dal.select_results(select_stmt=blocked_data_query)

#     _clean_up(dal)

#     # ensure blocked data has two rows, headers and data
#     assert len(results) == 2
#     assert results[1][1] is None
#     assert results[1][2] == pt2.get("zip")
