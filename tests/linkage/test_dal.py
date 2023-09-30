import datetime
import os
import pathlib
from phdi.linkage.dal import DataAccessLayer
from sqlalchemy import Engine, Table, select, text
from sqlalchemy.orm import scoped_session
from phdi.linkage.postgres_mpi import PGMPIConnectorClient


# [
#     [
#         "patient_id",
#         "dob",
#         "sex",
#         "mrn",
#         "last_name",
#         "given_name" "phone_number",
#         "phone_type",
#         "address_line_1",
#         "zip_code",
#         "city",
#         "state",
#         "person_id",
#     ],
#     [
#         UUID("80009abc-79d8-4e26-9d36-386edfcecdfa"),
#         datetime.date(1977, 11, 11),
#         "M",
#         "MRN-1234",
#         "Cat",
#         "Thomas",
#         "+14087775533",
#         "home",
#         "1313 Mocking Bird Lane",
#         "84607",
#         "Roy",
#         "UT",
#         UUID("80009abc-79d8-4e26-9d36-386edf979797"),
#     ],
#     [
#         UUID("80009abc-79d8-4e26-9d36-386edfcecdfa"),
#         datetime.date(1977, 11, 11),
#         "M",
#         "MRN-1234",
#         "Cat",
#         "Thomas",
#         "+18015553333",
#         "cell",
#         "1313 Mocking Bird Lane",
#         "84607",
#         "Roy",
#         "UT",
#         UUID("80009abc-79d8-4e26-9d36-386edf979797"),
#     ],
#     [
#         UUID("f85cfa46-9799-4f1a-ba3e-e97cca550138"),
#         datetime.date(1988, 1, 1),
#         "F",
#         "MRN-7788",
#         "Mouse",
#         "Jerry",
#         None,
#         None,
#         "8375 Jessie Lane",
#         "83642",
#         "Meridian",
#         "ID",
#         UUID("f85cfa46-9799-4f1a-ba3e-e97555599987"),
#     ],
# ]


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
        pg_connection.execute(text("""DROP TABLE IF EXISTS give_name CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS given_name CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS name CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS patient CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS person CASCADE;"""))
        pg_connection.commit()
        pg_connection.close()


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


def test_bulk_insert_dict():
    dal = _init_db()

    data_requested = {
        "patient": {
            "records": [
                {
                    "person_id": None,
                    "dob": "1977-11-11",
                    "sex": "male",
                    "race": "UNK",
                    "ethnicity": "UNK",
                }
            ],
        },
    }
    insert_result = dal.bulk_insert_dict(data_requested, False)

    assert insert_result == {"patient": {"results": []}}

    results = dal.select_results(select(dal.PATIENT_TABLE))
    assert len(results) == 2
    assert results[1][2] == datetime.date(1977, 11, 11)
    assert results[1][3] == "male"
    assert results[1][0] is not None

    data_requested = {
        "patient_id": None,
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
        query = dal.session.query(dal.PATIENT_TABLE)
        results = query.all()
        dal.session.close()
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
        "patient": {"table": dal.PATIENT_TABLE, "records": test_data2},
    }
    pks = dal.bulk_insert_dict(data_requested2, True)
    assert len(pks.get("patient").get("results")) == 2
    results = dal.select_results(select(dal.PATIENT_TABLE))
    assert len(results) == 4

    _clean_up(dal)


#     # TODO: saving this query here so it can be used in more robust tests
#     # in the near future:
#     #
#     # name_sub_query = (
#     #     select(
#     #         dal.GIVEN_NAME_TABLE.c.given_name.label("given_name"),
#     #         dal.GIVEN_NAME_TABLE.c.name_id.label("name_id"),
#     #     )
#     #     .where(dal.GIVEN_NAME_TABLE.c.given_name_index == 0)
#     #     .subquery()
#     # )

#     # id_sub_query = (
#     #     select(
#     #         dal.ID_TABLE.c.value.label("mrn"),
#     #         dal.ID_TABLE.c.patient_id.label("patient_id"),
#     #     )
#     #     .where(dal.ID_TABLE.c.type_code == "MR")
#     #     .subquery()
#     # )

#     # phone_sub_query = (
#     #     select(
#     #         dal.PHONE_TABLE.c.phone_number.label("phone_number"),
#     #         dal.PHONE_TABLE.c.type.label("phone_type"),
#     #         dal.PHONE_TABLE.c.patient_id.label("patient_id"),
#     #     )
#     #     .where(dal.PHONE_TABLE.c.type.in_(["home", "cell"]))
#     #     .subquery()
#     # )

#     # query = (
#     #     select(
#     #         dal.PATIENT_TABLE.c.patient_id,
#     #         dal.PATIENT_TABLE.c.dob,
#     #         dal.PATIENT_TABLE.c.sex,
#     #         id_sub_query.c.mrn,
#     #         dal.NAME_TABLE.c.last_name,
#     #         name_sub_query.c.given_name,
#     #         phone_sub_query.c.phone_number,
#     #         phone_sub_query.c.phone_type,
#     #         dal.ADDRESS_TABLE.c.line_1.label("address_line_1"),
#     #         dal.ADDRESS_TABLE.c.zip_code,
#     #         dal.ADDRESS_TABLE.c.city,
#     #         dal.ADDRESS_TABLE.c.state,
#     #         dal.PERSON_TABLE.c.person_id,
#     #     )
#     #     .outerjoin(
#     #         id_sub_query,
#     #     )
#     #     .outerjoin(dal.NAME_TABLE)
#     #     .outerjoin(name_sub_query)
#     #     .outerjoin(phone_sub_query)
#     #     .outerjoin(dal.ADDRESS_TABLE)
#     #     .outerjoin(dal.PERSON_TABLE)
#     # )


def test_get_table_by_name():
    dal = _init_db()
    table = dal.get_table_by_column("zip_code")
    assert table.name == "address"
    assert table.c is not None
    _clean_up(dal)

    dal2 = _init_db()
    dal2.initialize_schema()

    table = dal2.get_table_by_column("zip_code")
    assert table.name == "address"
    assert table.c is not None
    _clean_up(dal2)


def test_get_table_by_column():
    dal = _init_db()
    table = dal.get_table_by_column("zip_code")
    assert table.name == "address"
    assert table.c is not None
    _clean_up(dal)

    dal2 = _init_db()
    dal2.initialize_schema()

    table = dal2.get_table_by_column("zip_code")
    assert table.name == "address"
    assert table.c is not None
    _clean_up(dal2)


def test_does_table_have_column():
    dal = _init_db()
    assert dal.does_table_have_column(dal.GIVEN_NAME_TABLE, "patient_id") is False
    assert dal.does_table_have_column(dal.NAME_TABLE, "patient_id") is True
    _clean_up(dal)


def test_single_insert():
    dal = _init_db()

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

    pk = dal.single_insert(
        table=dal.PATIENT_TABLE,
        record=pt1,
        cte_query=None,
        return_pk=True,
        return_full=False,
    )
    assert pk is not None

    pk2 = dal.single_insert(
        table=dal.PATIENT_TABLE,
        record=pt2,
        cte_query=None,
        return_pk=False,
        return_full=False,
    )
    assert pk2 is None

    results = dal.select_results(select(dal.PATIENT_TABLE))
    assert len(results) == 3
    assert results[0][0] == "patient_id"
    assert results[1][0] == pk
    assert results[0][3] == "sex"
    assert results[1][3] == "male"
    assert results[2][3] == "female"

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
    pk = dal.single_insert(
        table=dal.PATIENT_TABLE,
        record=pt1,
        cte_query=None,
        return_pk=True,
        return_full=False,
    )
    dal.single_insert(
        table=dal.PATIENT_TABLE,
        record=pt2,
        cte_query=None,
        return_pk=False,
        return_full=False,
    )
    mpi = PGMPIConnectorClient()
    mpi._initialize_schema()
    blocked_data_query = mpi._generate_block_query(
        block_data, select(dal.PATIENT_TABLE)
    )
    results = dal.select_results(select_stmt=blocked_data_query)

    # ensure blocked data has two rows, headers and data
    assert len(results) == 2
    assert results[0][0] == "patient_id"
    assert results[1][0] == pk
    assert results[0][2] == "dob"
    assert results[1][2] == datetime.date(1977, 11, 11)
    assert results[0][3] == "sex"
    assert results[1][3] == "male"

    results2 = dal.select_results(
        select_stmt=blocked_data_query, include_col_header=False
    )

    # ensure blocked data has one row, just the data
    assert len(results2) == 1
    assert results2[0][0] == pk
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
        "ethnicity": "UNK",
    }
    pt2 = {
        "person_id": None,
        "dob": "1988-01-01",
        "sex": "female",
        "race": "UNK",
        "ethnicity": "UNK",
    }
    pat_data = [pt1, pt2]
    pk_list = dal.bulk_insert_list(dal.PATIENT_TABLE, pat_data, True)

    assert len(pk_list) == 2

    results = dal.select_results(select(dal.PATIENT_TABLE))
    assert len(results) == 3
    assert results[0][0] == "patient_id"
    assert results[1][0] == pk_list[0]
    assert results[2][0] == pk_list[1]
    assert results[0][3] == "sex"
    assert results[1][3] == "male"
    assert results[2][3] == "female"

    pat_data2 = [pt1, pt2]
    pk_list2 = dal.bulk_insert_list(dal.PATIENT_TABLE, pat_data2, False)
    assert len(pk_list2) == 0

    _clean_up(dal)
