import datetime
import json
import os
import pathlib
import re
import uuid

import pytest
from app.linkage.dal import DataAccessLayer
from app.linkage.mpi import DIBBsMPIConnectorClient
from app.utils import _clean_up
from sqlalchemy import Select
from sqlalchemy import select
from sqlalchemy import text

patient_resource = json.load(
    open(
        pathlib.Path(__file__).parent.parent.parent.parent
        / "containers"
        / "record-linkage"
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

    return DIBBsMPIConnectorClient()


def test_get_blocked_data():
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
        table=MPI.dal.PATIENT_TABLE, records=test_data, return_primary_keys=True
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
        table=MPI.dal.PATIENT_TABLE, records=test_data, return_primary_keys=True
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
    MPI: DIBBsMPIConnectorClient = _init_db()
    base_query = MPI._get_base_query()
    expected_query = """
        SELECT
            patient.patient_id, patient.person_id, patient.dob AS birthdate,
            patient.sex, ident_subq.mrn, name.last_name,
            array_agg(
                given_name.given_name ORDER BY given_name.given_name_index ASC
            ) AS given_name,
            address.line_1 AS address, address.zip_code AS zip, address.city,
            address.state
        FROM patient
        LEFT OUTER JOIN (
            SELECT
                identifier.patient_identifier AS mrn,
                identifier.patient_id AS patient_id
            FROM identifier
            WHERE identifier.type_code = :type_code_1
        ) AS ident_subq ON patient.patient_id = ident_subq.patient_id
        LEFT OUTER JOIN name ON patient.patient_id = name.patient_id
        LEFT OUTER JOIN given_name ON name.name_id = given_name.name_id
        LEFT OUTER JOIN address ON patient.patient_id = address.patient_id
        GROUP BY
            patient.patient_id, patient.person_id, birthdate, patient.sex,
            ident_subq.mrn, name.last_name, name.name_id, address, zip,
            address.city, address.state
        """
    assert base_query is not None
    assert isinstance(base_query, Select)
    _clean_up(MPI.dal)
    assert re.sub(r"\s+", "", str(base_query)) == re.sub(r"\s+", "", expected_query)


def test_organize_block_criteria():
    MPI: DIBBsMPIConnectorClient = _init_db()
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
        block_criteria=block_data, table_name="patient"
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
        + "(SELECT DISTINCT patient.patient_id AS patient_id"
        + "FROM patient"
        + "WHERE patient.dob = '1977-11-11' AND patient.sex = 'M')"
        + "SELECT patient.patient_id, patient.person_id, patient.dob,"
        + "patient.sex, patient.race, patient.ethnicity"
        + "FROM patient JOIN patient_cte ON "
        + "patient_cte.patient_id = patient.patient_id"
    )
    # ensure query has the proper where clause added
    assert re.sub(r"\s+", "", str(my_query)) == re.sub(r"\s+", "", expected_result)

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
        "WITH given_name_cte AS "
        "(SELECT DISTINCT name.patient_id AS patient_id FROM name JOIN "
        "(SELECT given_name.given_name_id AS given_name_id, "
        "given_name.name_id AS name_id, given_name.given_name AS given_name, "
        "given_name.given_name_index AS given_name_index FROM given_name "
        "WHERE given_name.given_name = 'Homer') AS given_name_cte_subq "
        "ON name.name_id = given_name_cte_subq.name_id), name_cte AS "
        "(SELECT DISTINCT name.patient_id AS patient_id FROM name WHERE "
        "name.last_name = 'Simpson') SELECT patient.patient_id, patient.person_id, "
        "patient.dob, patient.sex, patient.race, patient.ethnicity FROM patient JOIN "
        "given_name_cte ON given_name_cte.patient_id = patient.patient_id JOIN "
        "name_cte ON name_cte.patient_id = patient.patient_id"
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
    _init_db()
    MPI = DIBBsMPIConnectorClient()

    assert MPI is not None
    assert isinstance(MPI, DIBBsMPIConnectorClient)
    assert MPI.dal is not None
    assert isinstance(MPI.dal, DataAccessLayer)


def test_insert_matched_patient():
    MPI = _init_db()

    result = MPI.insert_matched_patient(patient_resource)
    assert result is not None

    person_rec = MPI.dal.select_results(select(MPI.dal.PERSON_TABLE))
    patient_rec = MPI.dal.select_results(select(MPI.dal.PATIENT_TABLE))
    name_rec = MPI.dal.select_results(select(MPI.dal.NAME_TABLE))
    given_name_rec = MPI.dal.select_results(select(MPI.dal.GIVEN_NAME_TABLE))
    address_rec = MPI.dal.select_results(select(MPI.dal.ADDRESS_TABLE))
    phone_rec = MPI.dal.select_results(select(MPI.dal.PHONE_TABLE))
    id_rec = MPI.dal.select_results(select(MPI.dal.ID_TABLE))

    assert len(person_rec) == 2
    assert len(patient_rec) == 2
    assert len(name_rec) == 2
    assert len(given_name_rec) == 3
    assert len(address_rec) == 2
    assert len(phone_rec) == 2
    assert len(id_rec) == 2

    _clean_up(MPI.dal)

    MPI = _init_db()

    external_person_id = "EXT-1233456"
    result = MPI.insert_matched_patient(
        patient_resource=patient_resource,
        person_id=None,
        external_person_id=external_person_id,
    )
    assert result is not None

    EXTERNAL_PERSON_rec = MPI.dal.select_results(select(MPI.dal.EXTERNAL_PERSON_TABLE))
    person_rec = MPI.dal.select_results(select(MPI.dal.PERSON_TABLE))
    patient_rec = MPI.dal.select_results(select(MPI.dal.PATIENT_TABLE))
    name_rec = MPI.dal.select_results(select(MPI.dal.NAME_TABLE))
    given_name_rec = MPI.dal.select_results(select(MPI.dal.GIVEN_NAME_TABLE))
    address_rec = MPI.dal.select_results(select(MPI.dal.ADDRESS_TABLE))
    phone_rec = MPI.dal.select_results(select(MPI.dal.PHONE_TABLE))
    id_rec = MPI.dal.select_results(select(MPI.dal.ID_TABLE))

    assert len(person_rec) == 2
    assert len(EXTERNAL_PERSON_rec) == 2
    assert EXTERNAL_PERSON_rec[1][2] == external_person_id
    assert EXTERNAL_PERSON_rec[1][3].__str__() == "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380b79"
    assert len(patient_rec) == 2
    assert len(name_rec) == 2
    assert len(given_name_rec) == 3
    assert len(address_rec) == 2
    assert len(phone_rec) == 2
    assert len(id_rec) == 2

    _clean_up(MPI.dal)

    # Test for missing external_person_id
    MPI = _init_db()

    result = MPI.insert_matched_patient(
        patient_resource=patient_resource,
        person_id=None,
        external_person_id=None,
    )
    assert result is not None

    EXTERNAL_PERSON_rec = MPI.dal.select_results(select(MPI.dal.EXTERNAL_PERSON_TABLE))
    person_rec = MPI.dal.select_results(select(MPI.dal.PERSON_TABLE))
    patient_rec = MPI.dal.select_results(select(MPI.dal.PATIENT_TABLE))
    name_rec = MPI.dal.select_results(select(MPI.dal.NAME_TABLE))
    given_name_rec = MPI.dal.select_results(select(MPI.dal.GIVEN_NAME_TABLE))
    address_rec = MPI.dal.select_results(select(MPI.dal.ADDRESS_TABLE))
    phone_rec = MPI.dal.select_results(select(MPI.dal.PHONE_TABLE))
    id_rec = MPI.dal.select_results(select(MPI.dal.ID_TABLE))

    assert len(person_rec) == 2
    assert len(EXTERNAL_PERSON_rec) == 1
    assert len(patient_rec) == 2
    assert len(name_rec) == 2
    assert len(given_name_rec) == 3
    assert len(address_rec) == 2
    assert len(phone_rec) == 2
    assert len(id_rec) == 2

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

    # ensure blocked data has two rows, header and data
    assert len(blocked_data) == 2
    assert blocked_data[1][1] is None
    assert blocked_data[1][0] == pks_pt[0]
    assert blocked_data[1][0] != pks_pt2[0]
    assert blocked_data[1][2] == datetime.date(1983, 2, 1)
    assert blocked_data[1][3] == "male"
    assert blocked_data[1][5] == "Shepard"
    assert blocked_data[1][6] == ["Johnathon", "Maurice"]
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


@pytest.mark.parametrize(
    "given_name_sets,expected_given_name_counts",
    [
        (["Brian", "Peter", "George", "St. John", "le Baptiste", "de la Salle"], 6),
        (["Jorge", "Francisco", "Isidoro", "Luis"], 4),
        (["John", "Ronald", "Reuel"], 3),
        (
            [
                "Pablo",
                "Diego",
                "José",
                "Francisco",
                "de Paula",
                "Juan",
                "Nepomuceno",
                "María",
                "de los Remedios",
                "Cipriano",
                "de la Santísima",
                "Trinidad",
            ],
            12,
        ),
    ],
)
def test_extract_given_names(given_name_sets, expected_given_name_counts):
    MPI = _init_db()
    name_id = uuid.uuid4()
    given_name_records = MPI._extract_given_names(given_name_sets, name_id)

    assert len(given_name_records) == expected_given_name_counts

    for idx, record in enumerate(given_name_records):
        assert record["name_id"] == name_id
        assert record["given_name_index"] == idx

    _clean_up(MPI.dal)


@pytest.mark.parametrize(
    "given_name_sets_1, given_name_sets_2",
    [
        (
            ["Brian", "Peter", "George"],
            ["Brian", "Peter", "George", "St. John", "le Baptiste", "de la Salle"],
        ),
        (["Jorge", "Luis", "Borges"], ["Jorge", "Francisco", "Isidoro", "Luis"]),
        (["John", "Ronald", "Reuel"], ["John", "Ronald", "Reuel", "Tolkien"]),
        (
            ["Pablo", "Diego", "José"],
            [
                "Pablo",
                "Diego",
                "José",
                "Francisco",
                "de Paula",
                "Juan",
                "Nepomuceno",
                "María",
                "de los Remedios",
                "Cipriano",
                "de la Santísima",
                "Trinidad",
            ],
        ),
    ],
)
def test_given_names_association(given_name_sets_1, given_name_sets_2):
    """
    This function tests that different sets of a person's given names
    are associated differently.
    """
    MPI = _init_db()

    name_id_1 = uuid.uuid4()
    name_id_2 = uuid.uuid4()

    given_name_records_1 = MPI._extract_given_names(given_name_sets_1, name_id_1)
    given_name_records_2 = MPI._extract_given_names(given_name_sets_2, name_id_2)

    assert given_name_records_1[0]["name_id"] != given_name_records_2[0]["name_id"]

    _clean_up(MPI.dal)


def test_get_mpi_records():
    MPI = _init_db()

    patients = json.load(
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "linkage"
            / "patient_bundle_to_link_with_mpi.json"
        )
    )
    patients = patients["entry"]
    patients = [
        p.get("resource")
        for p in patients
        if p.get("resource", {}).get("resourceType", "") == "Patient"
    ][:2]

    # Success
    records_for_insert = MPI._get_mpi_records(patients[0])
    assert isinstance(records_for_insert, dict)
    assert "given_name" in records_for_insert.keys()
    assert len(records_for_insert["given_name"]) == 2

    # Non-patient resource
    patients[0]["resourceType"] = "Not Patient"
    records_for_insert = MPI._get_mpi_records(patients[0])
    assert bool(records_for_insert) is False

    # Multiple names in a single resource
    second_name = {
        "family": "Sheperd",
        "given": ["John", "Tiberius"],
        "use": "official",
    }
    patients[1]["name"].append(second_name)
    records_for_insert = MPI._get_mpi_records(patients[1])
    assert len(records_for_insert["given_name"]) == 4

    # Multiple names in a single resource with some values missing
    third_name = {
        "family": None,
        "given": ["John", "Tiberius"],
        "use": "official",
    }
    patients[1]["name"].append(third_name)
    records_for_insert = MPI._get_mpi_records(patients[1])
    assert len(records_for_insert["name"]) == 3
    assert len(records_for_insert["given_name"]) == 6

    # Multiple names in a single resource with some values missing
    fourth_name = {
        "family": None,
        "use": "official",
    }
    patients[1]["name"].append(fourth_name)
    records_for_insert = MPI._get_mpi_records(patients[1])
    assert len(records_for_insert["name"]) == 4
    assert len(records_for_insert["given_name"]) == 7

    # Check that patient_id is inserted properly across appropriate tables
    patient_id = patients[1]["id"]
    assert records_for_insert["patient"][0]["patient_id"] == patient_id
    assert records_for_insert["name"][0]["patient_id"] == patient_id

    # Check that new patient_id is created if no id is present in incoming record
    patients[1]["id"] = None
    records_for_insert = MPI._get_mpi_records(patients[1])
    assert records_for_insert["patient"][0]["patient_id"] is not None
    assert (
        records_for_insert["patient"][0]["patient_id"]
        == records_for_insert["address"][0]["patient_id"]
    )

    _clean_up(MPI.dal)


def test_get_external_source_id():
    MPI = _init_db()

    # Success
    external_source_id = MPI._get_external_source_id("IRIS")
    assert isinstance(external_source_id, uuid.UUID)

    # Failure
    external_source_id = MPI._get_external_source_id("Not a source")
    assert external_source_id is None

    # Confirm cache is working
    MPI._get_external_source_id("IRIS")
    assert MPI._get_external_source_id.cache_info().hits == 1
    _clean_up(MPI.dal)
