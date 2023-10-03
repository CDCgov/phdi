import datetime
import json
import os
import pathlib
import re
import pytest

from sqlalchemy import Select, select, text
from phdi.linkage.postgres_mpi import PGMPIConnectorClient
from phdi.linkage.dal import DataAccessLayer

patient_resource = json.load(
    open(
        pathlib.Path(__file__).parent.parent.parent
        / "tests"
        / "assets"
        / "general"
        / "patient_resource_w_extensions.json"
    )
)


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
    MPI._initialize_schema()
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
    pks = MPI.dal.bulk_insert_list(
        table=MPI.dal.PATIENT_TABLE, records=test_data, return_pks=True
    )
    assert len(pks) == 2

    blocked_data = MPI.get_block_data(block_data)

    _clean_up(MPI.dal)

    # ensure blocked data has two rows, headers and data
    assert len(blocked_data) == 2
    assert blocked_data[1][0] == pks[0]
    assert blocked_data[0][0] == "patient_id"
    assert blocked_data[1][1] is None
    assert blocked_data[0][1] == "person_id"
    assert blocked_data[1][2].strftime("%Y-%m-%d") == "1977-11-11"
    assert blocked_data[0][2] == "birthdate"
    assert len(blocked_data[0]) == 11


def test_block_data_failures():
    MPI = _init_db()
    block_data = {}
    blocked_data = None
    # test empty block vals
    with pytest.raises(ValueError) as e:
        blocked_data = MPI.get_block_data(block_data)
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
    pks = MPI.dal.bulk_insert_list(
        table=MPI.dal.PATIENT_TABLE, records=test_data, return_pks=True
    )
    blocked_data = MPI.get_block_data(block_data)
    assert len(pks) == 2

    _clean_up(MPI.dal)

    # ensure blocked data has two rows, headers and data
    # testing to ensure that invalid block vals are skipped
    #  and not used in the filtering of the query
    assert len(blocked_data) == 2
    assert blocked_data[1][0] == pks[0]
    assert blocked_data[0][0] == "patient_id"
    assert blocked_data[1][1] is None
    assert blocked_data[0][1] == "person_id"
    assert blocked_data[1][2].strftime("%Y-%m-%d") == "1977-11-11"
    assert blocked_data[0][2] == "birthdate"
    assert len(blocked_data[0]) == 11


def test_get_base_query():
    MPI: PGMPIConnectorClient = _init_db()
    base_query = MPI._get_base_query()
    expected_query = (
        "SELECT patient.patient_id, person.person_id, patient.dob AS"
        + " birthdate, patient.sex, ident_subq.mrn, name.last_name, "
        + "gname_subq.given_name AS first_name, address.line_1 AS "
        + "address, address.zip_code AS zip, address.city, address.state"
        + "FROM patient LEFT OUTER JOIN (SELECT identifier.value AS mrn,"
        + " identifier.patient_id AS patient_id"
        + "FROM identifier"
        + "WHERE identifier.type_code = :type_code_1) AS ident_subq ON "
        + "patient.patient_id = ident_subq.patient_id LEFT OUTER JOIN "
        + "name ON patient.patient_id = name.patient_id LEFT OUTER "
        + "JOIN (SELECT given_name.given_name AS given_name, "
        + "given_name.name_id AS name_id"
        + "FROM given_name"
        + "WHERE given_name.given_name_index = :given_name_index_1)"
        + " AS gname_subq ON name.name_id = gname_subq.name_id LEFT OUTER JOIN"
        + " address ON patient.patient_id = address.patient_id LEFT OUTER"
        + " JOIN person ON person.person_id = patient.person_id"
    )
    assert base_query is not None
    assert isinstance(base_query, Select)
    _clean_up(MPI.dal)
    assert re.sub(r"\s+", "", str(base_query)) == re.sub(r"\s+", "", expected_query)


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

    expected_result2 = (
        "WITH given_name_cte AS"
        + "(SELECT name.patient_id AS patient_id"
        + "FROM name JOIN (SELECT given_name.given_name_id "
        + "AS given_name_id, given_name.name_id AS name_id, "
        + "given_name.given_name AS given_name, "
        + "given_name.given_name_index AS given_name_index"
        + "FROM given_name"
        + "WHERE given_name.given_name = 'Homer') "
        + "AS given_name_cte_subq ON name.name_id = given_name_cte_subq.name_id"
        + "WHERE name.name_id = given_name_cte_subq.name_id),"
        + "name_cte AS"
        + "(SELECT name.patient_id AS patient_id"
        + "FROM name"
        + "WHERE name.last_name = 'Simpson')"
        + "SELECT patient.patient_id, patient.person_id,"
        + " patient.dob, patient.sex, patient.race, patient.ethnicity"
        + "FROM patient JOIN given_name_cte ON "
        + "given_name_cte.patient_id = patient.patient_id "
        + "JOIN name_cte ON name_cte.patient_id = patient.patient_id"
    )

    base_query2 = select(MPI.dal.PATIENT_TABLE)
    my_query2 = MPI._generate_block_query(block_data2, base_query2)

    _clean_up(MPI.dal)
    assert re.sub(r"\s+", "", str(my_query2)) == re.sub(r"\s+", "", expected_result2)


def test_init():
    os.environ = {
        "mpi_dbname": "testdb",
        "mpi_user": "postgres",
        "mpi_password": "pw",
        "mpi_host": "localhost",
        "mpi_port": "5432",
        "mpi_db_type": "postgres",
    }

    MPI = PGMPIConnectorClient()

    assert MPI is not None
    assert isinstance(MPI, PGMPIConnectorClient)
    assert MPI.dal is not None
    assert isinstance(MPI.dal, DataAccessLayer)


def test_insert_matched_patient():
    MPI = _init_db()

    result = MPI.insert_matched_patient(patient_resource)
    print(f"RESULT: {result}")
    assert result is not None
    assert not result[0]
    assert result[1] is not None

    person_rec = MPI.dal.select_results(select(MPI.dal.EXT_PERSON_TABLE), False)
    patient_rec = MPI.dal.select_results(select(MPI.dal.PATIENT_TABLE), False)
    name_rec = MPI.dal.select_results(select(MPI.dal.NAME_TABLE), False)
    given_name_rec = MPI.dal.select_results(select(MPI.dal.GIVEN_NAME_TABLE), False)
    address_rec = MPI.dal.select_results(select(MPI.dal.ADDRESS_TABLE), False)
    phone_rec = MPI.dal.select_results(select(MPI.dal.PHONE_TABLE), False)
    id_rec = MPI.dal.select_results(select(MPI.dal.ID_TABLE), False)

    assert len(person_rec) > 0
    assert len(patient_rec) > 0
    assert len(name_rec) > 0
    assert len(given_name_rec) > 0
    assert len(address_rec) > 0
    assert len(phone_rec) > 0
    assert len(id_rec) > 0

    _clean_up(MPI.dal)


def test_get_person():
    MPI = _init_db()
    result = MPI._get_person_id(person_id=None, external_person_id=None)
    assert result is not None

    results = MPI.dal.select_results(select(MPI.dal.PERSON_TABLE))
    assert results[1][0] == result

    result2 = MPI._get_person_id(person_id=result, external_person_id=None)
    assert result2 == result
    results2 = MPI.dal.select_results(select(MPI.dal.EXT_PERSON_TABLE))
    assert len(results2) == 1
    assert results2[0][0] == "external_id"

    result3 = MPI._get_person_id(person_id=result, external_person_id="MYEXTID-123")
    assert result3 == result
    results3 = MPI.dal.select_results(select(MPI.dal.EXT_PERSON_TABLE))
    print(f"RES3: {results3}")
    assert len(results3) == 2
    assert results3[0][0] == "external_id"
    assert results3[1][0] is not None
    assert results3[1][1] == result3
    assert results3[1][2] == "MYEXTID-123"

    result4 = MPI._get_person_id(person_id=None, external_person_id="MYEXTID-789")
    assert result4 is not None
    assert result4 != result
    query = select(MPI.dal.EXT_PERSON_TABLE).where(
        text(f"{MPI.dal.EXT_PERSON_TABLE.name}.external_person_id = 'MYEXTID-789'")
    )
    results4 = MPI.dal.select_results(query)
    assert len(results4) == 2
    assert results4[0][0] == "external_id"
    assert results4[1][0] is not None
    assert results4[1][1] == result4
    assert results4[1][2] == "MYEXTID-789"

    _clean_up(MPI.dal)


def test_block_data_with_transform():
    MPI = _init_db()
    data_requested = {
        "first_name": {"value": "John", "transformation": "first4"},
        "last_name": {"value": "Shep", "transformation": "first4"},
        "address": {"value": "e St", "transformation": "last4"},
    }
    test_data = []
    pt1 = {"person_id": None, "dob": "1983-02-01", "sex": "male"}

    test_data.append(pt1)
    pks_pt = MPI.dal.bulk_insert_list(MPI.dal.PATIENT_TABLE, test_data, True)
    ln1 = [{"patient_id": pks_pt[0], "last_name": "Shepard"}]
    pks_ln = MPI.dal.bulk_insert_list(MPI.dal.NAME_TABLE, ln1, True)

    gn1 = {"name_id": pks_ln[0], "given_name": "Johnathon", "given_name_index": 0}
    gn2 = {"name_id": pks_ln[0], "given_name": "Maurice", "given_name_index": 1}
    test_data_gn = [gn1, gn2]
    MPI.dal.bulk_insert_list(MPI.dal.GIVEN_NAME_TABLE, test_data_gn, False)

    add1 = [
        {
            "patient_id": pks_pt[0],
            "line_1": "1313 e St",
            "city": "Fakeville",
            "state": "NY",
            "zip_code": "10001-0001",
            "type": "home",
        }
    ]
    MPI.dal.bulk_insert_list(MPI.dal.ADDRESS_TABLE, add1, False)

    pt2 = [{"person_id": None, "dob": "1973-03-17", "sex": "male"}]
    pks_pt2 = MPI.dal.bulk_insert_list(MPI.dal.PATIENT_TABLE, pt2, True)

    blocked_data = MPI.get_block_data(data_requested)

    _clean_up(MPI.dal)

    # ensure blocked data has two rows, headers and data
    assert len(blocked_data) == 2
    assert blocked_data[1][1] is None
    assert blocked_data[1][0] == pks_pt[0]
    assert blocked_data[1][0] != pks_pt2[0]
    assert blocked_data[1][2] == datetime.date(1983, 2, 1)
    assert blocked_data[1][3] == "male"
    assert blocked_data[1][7] == add1[0].get("line_1")
    assert blocked_data[1][8] == add1[0].get("zip_code")


def test_generate_dict_record_from_results():
    MPI = _init_db()
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
    pk_list = MPI.dal.bulk_insert_list(MPI.dal.PATIENT_TABLE, pat_data, True)
    results = MPI.dal.select_results(select(MPI.dal.PATIENT_TABLE))

    records = MPI._generate_dict_record_from_results(results)

    assert len(records) == 2
    assert records[0]["patient_id"] == pk_list[0]
    assert records[1]["patient_id"] == pk_list[1]

    _clean_up(MPI.dal)
