from phdi.linkage.postgres import DIBBsConnectorClient
import pathlib
import pytest
import json
import copy


def _create_valid_mpi_client():
    return DIBBsConnectorClient(
        database="testdb",
        user="postgres",
        password="pw",
        host="localhost",
        port="5432",
        patient_table="test_patient_mpi",
        person_table="test_person_mpi",
        external_person_id_table="test_external_id_mpi",
        external_source_table="test_external_source_mpi",
    )


def _create_tables(postgres_client=None):
    if postgres_client is None:
        postgres_client = _create_valid_mpi_client()
    postgres_client.connection = postgres_client.get_connection()
    postgres_client.cursor = postgres_client.connection.cursor()

    funcs = {
        "drop tables": (
            f"""
        DROP TABLE IF EXISTS {postgres_client.patient_table};
        DROP TABLE IF EXISTS {postgres_client.person_table};
        """
        ),
        "create_patient": (
            """
            BEGIN;

            CREATE EXTENSION IF NOT EXISTS "uuid-ossp";"""
            + f"CREATE TABLE IF NOT EXISTS {postgres_client.patient_table} "
            + "(patient_id UUID DEFAULT uuid_generate_v4 (), person_id UUID, "
            + "patient_resource JSONB);"
        ),
        "create_person": (
            """
            BEGIN;

            CREATE EXTENSION IF NOT EXISTS "uuid-ossp";"""
            + f"CREATE TABLE IF NOT EXISTS {postgres_client.person_table} "
            + "(person_id UUID DEFAULT uuid_generate_v4 ());"
        ),
        "create_external_sources": (
            """
            BEGIN;

            CREATE EXTENSION IF NOT EXISTS "uuid-ossp";"""
            + f"CREATE TABLE IF NOT EXISTS {postgres_client.external_source_table} "
            + "(external_source_key UUID DEFAULT uuid_generate_v4 (), "
            + "external_source_name VARCHAR(100), "
            + "external_source_description VARCHAR(500));"
        ),
        "create_external_ids": (
            """
            BEGIN;
            
            CREATE EXTENSION IF NOT EXISTS "uuid-ossp";"""
            + f"CREATE TABLE IF NOT EXISTS {postgres_client.external_person_id_table} "
            + "(external_id_key UUID DEFAULT uuid_generate_v4 (), "
            + "person_id UUID, "
            + "external_person_id VARCHAR(100), "
            + f"external_source_key UUID);"
        ),
    }

    for command, statement in funcs.items():
        try:
            postgres_client.cursor.execute(statement)
            postgres_client.connection.commit()
        except Exception as e:
            print(f"{command} was unsuccessful")
            print(e)
            postgres_client.connection.rollback()

    return postgres_client


def _drop_tables(postgres_client):
    postgres_client.connection = postgres_client.get_connection()
    postgres_client.cursor = postgres_client.connection.cursor()
    postgres_client.cursor.execute(
        f"DROP TABLE IF EXISTS {postgres_client.external_person_id_table}"
    )
    postgres_client.connection.commit()
    postgres_client.cursor.execute(
        f"DROP TABLE IF EXISTS {postgres_client.external_source_table}"
    )
    postgres_client.connection.commit()
    postgres_client.cursor.execute(
        f"DROP TABLE IF EXISTS {postgres_client.person_table}"
    )
    postgres_client.connection.commit()
    postgres_client.cursor.execute(
        f"DROP TABLE IF EXISTS {postgres_client.patient_table}"
    )
    postgres_client.connection.commit()
    postgres_client.cursor.close()
    postgres_client.connection.close()


def test_postgres_connection():
    postgres_client = _create_valid_mpi_client()
    postgres_client.connection = postgres_client.get_connection()
    postgres_client.cursor = postgres_client.connection.cursor()

    assert postgres_client.connection is not None
    postgres_client.cursor.close()
    postgres_client.connection.close()


def test_generate_block_query():
    postgres_client = _create_valid_mpi_client()
    block_vals = {
        "zip": {"value": "90120-1001"},
        "last_name": {"value": "GONZ", "transformation": "first4"},
    }

    generated_query, generated_data = postgres_client._generate_block_query(block_vals)
    assert (
        generated_query.__str__()
        == "Composed([SQL('SELECT patient_id, person_id, jsonb_path_query_array(patient_resource,%s) as address, jsonb_path_query_array(patient_resource,%s) as birthdate, jsonb_path_query_array(patient_resource,%s) as city, jsonb_path_query_array(patient_resource,%s) as first_name, jsonb_path_query_array(patient_resource,%s) as last_name, jsonb_path_query_array(patient_resource,%s) as mrn, jsonb_path_query_array(patient_resource,%s) as sex, jsonb_path_query_array(patient_resource,%s) as state, jsonb_path_query_array(patient_resource,%s) as zip FROM '), Identifier('test_patient_mpi'), SQL(\" WHERE CAST(jsonb_path_query_array(patient_resource, %s) as VARCHAR)= '[true]' AND CAST(jsonb_path_query_array(patient_resource, %s) as VARCHAR)= '[true]';\")])"  # noqa
    )
    assert generated_data == [
        "$.address[*].line",
        "$.birthDate",
        "$.address[*].city",
        "$.name[*].given",
        "$.name[*].family",
        '$.identifier ?(@.type.coding[0].code=="MR").value',
        "$.gender",
        "$.address[*].state",
        "$.address[*].postalCode",
        '$.address[*].postalCode like_regex "90120-1001"',
        '$.name[*].family starts with "GONZ"',
    ]

    # Test bad block_data
    block_vals = {"bad_block_column": "90120-1001"}
    with pytest.raises(ValueError) as e:
        blocked_data = postgres_client._generate_block_query(block_vals)
        assert f"""`{list(block_vals.keys())[0]}`
        not supported for blocking at this time.""" in str(
            e
        )
        assert blocked_data is None


def test_block_data():
    postgres_client = _create_valid_mpi_client()

    raw_bundle = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "tests"
            / "assets"
            / "general"
            / "patient_bundle.json"
        )
    )
    patient_resource = raw_bundle.get("entry")[1].get("resource")
    patient_resource["id"] = "4d88cd35-5ee7-4419-a847-2818fdfeec50"

    # Test for invalid block data
    block_vals = {}
    with pytest.raises(ValueError) as e:
        blocked_data = postgres_client.block_data(block_vals)
        assert "`block_data` cannot be empty." in str(e.value)

    block_vals = {"last_name": {"value": patient_resource["name"][0]["family"]}}
    _create_tables(postgres_client)

    funcs = {
        "insert": (
            f"""INSERT INTO {postgres_client.patient_table}
             (person_id, patient_resource) """
            + f"""VALUES ('4d88cd35-5ee7-4419-a847-2818fdfeec38',
            '{json.dumps(patient_resource)}');"""
        ),
    }
    for command, statement in funcs.items():
        try:
            postgres_client.cursor.execute(statement)
            postgres_client.connection.commit()
        except Exception as e:
            print(f"{command} was unsuccessful")
            print(e)
            postgres_client.connection.rollback()

    blocked_data = postgres_client.block_data(block_vals)

    # Assert that all returned data matches blocking criterion
    for row in blocked_data[1:]:
        assert block_vals["last_name"]["value"] in row[-5]

    # Assert returned data are LoL
    assert type(blocked_data[1]) is list
    _drop_tables(postgres_client)


def test_dibbs_blocking():
    postgres_client = _create_valid_mpi_client()

    raw_bundle = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "tests"
            / "assets"
            / "general"
            / "patient_bundle.json"
        )
    )

    patient_resource = raw_bundle.get("entry")[1].get("resource")
    patient_resource_2 = copy.deepcopy(patient_resource)
    patient_resource["id"] = "4d88cd35-5ee7-4419-a847-2818fdfeec50"
    patient_resource_2["id"] = "4d88cd35-5ee7-4419-a847-2818fdfeec51"
    patient_resource_2["identifier"][0]["value"] = "4455"
    # Add 2nd MRN to patient resource
    another_mrn = {
        "value": "78910",
        "type": {
            "coding": [
                {
                    "code": "MR",
                    "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                    "display": "Medical record number",
                }
            ]
        },
        "system": "other system",
    }
    patient_resource["identifier"].append(another_mrn)

    _create_tables(postgres_client)
    funcs = {
        "insert": (
            f"""INSERT INTO {postgres_client.patient_table}
             (person_id, patient_resource) """
            + f"""VALUES ('4d88cd35-5ee7-4419-a847-2818fdfeec38',
            '{json.dumps(patient_resource)}');"""
        ),
        "insert_2": (
            f"""INSERT INTO {postgres_client.patient_table}
             (person_id, patient_resource) """
            + f"""VALUES ('4d88cd35-5ee7-4419-a847-2818fdfeec39',
            '{json.dumps(patient_resource_2)}');"""
        ),
    }
    for command, statement in funcs.items():
        try:
            postgres_client.cursor.execute(statement)
            postgres_client.connection.commit()
        except Exception as e:
            print(f"{command} was unsuccessful")
            print(e)
            postgres_client.connection.rollback()

    # DIBBS Pass 1 Blocks
    block_vals_pass1 = {
        "mrn": {
            "value": patient_resource["identifier"][0]["value"][-4:],
            "transformation": "last4",
        },
        "address": {
            "value": patient_resource["address"][0]["line"][0][0:4],
            "transformation": "first4",
        },
    }
    blocked_data_pass1 = postgres_client.block_data(block_vals_pass1)

    # Assert only patient 1 is returned & matches on block criteria
    assert len(blocked_data_pass1[1:]) == 1
    # Assert matching on last4 of MRN
    assert patient_resource["identifier"][0]["value"][-4:] in [
        b[-4:] for b in blocked_data_pass1[1][-4]
    ]
    # Assert matching on 1st 4 of address
    assert patient_resource["address"][0]["line"][0][0:4] in [
        b[:4] for b in blocked_data_pass1[1][2][0]
    ]

    # DIBBS Pass 2 Blocks
    block_vals_pass2 = {
        "first_name": {
            "value": patient_resource["name"][0]["given"][0][0:4],
            "transformation": "first4",
        },
        "last_name": {
            "value": patient_resource["name"][0]["family"][0:4],
            "transformation": "first4",
        },
    }

    blocked_data_pass2 = postgres_client.block_data(block_vals_pass2)

    # Assert both patients are  returned & matches on block criteria
    assert len(blocked_data_pass2[1:]) == 2
    # Assert all returned records match on first 4 characters of first and last names
    for record in blocked_data_pass2[1:]:
        assert patient_resource["name"][0]["given"][0][0:4] in [
            fname[0:4] for fname in record[5][0][0:4]
        ]
        assert patient_resource["name"][0]["family"][0:4] == record[6][0][0:4]

    _drop_tables(postgres_client)


def test_insert_match_patient():
    postgres_client = _create_valid_mpi_client()
    postgres_client.connection = postgres_client.get_connection()
    postgres_client.cursor = postgres_client.connection.cursor()

    raw_bundle = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "tests"
            / "assets"
            / "general"
            / "patient_bundle.json"
        )
    )

    patient_resource = raw_bundle.get("entry")[1].get("resource")
    patient_resource["id"] = "4d88cd35-5ee7-4419-a847-2818fdfeec50"

    _create_tables(postgres_client)
    funcs = {
        "insert_patient": (
            f"""INSERT INTO {postgres_client.patient_table} (patient_id, person_id, """
            + "patient_resource) "
            + """VALUES
                ('4d88cd35-5ee7-4419-a847-2818fdfeec38',
                'ce02326f-7ecd-47ea-83eb-71e8d7c39131',
                '{"FIRST4":"JOHN","LAST4":"SMIT","ZIP":"90120-1001"}'),
                ('4d88cd35-5ee7-4419-a847-2818fdfeec39',
                'cb9dc379-38a9-4ed6-b3a7-a8a3db0e9e6c',
                '{"FIRST4":"JOSE","LAST4":"GONZ","ZIP":"90120-1001"}'),
                ('4d88cd35-5ee7-4419-a847-2818fdfeec40',
                'c2477ae3-d554-4979-bd92-893076640ffb',
                '{"FIRST4":"MARI","LAST4":"GONZ","ZIP":"90120-1001"}');"""
        ),
        "insert_person": (
            f"""INSERT INTO {postgres_client.person_table} (person_id) """
            + """VALUES ('ce02326f-7ecd-47ea-83eb-71e8d7c39131'),
             ('cb9dc379-38a9-4ed6-b3a7-a8a3db0e9e6c'),
             ('c2477ae3-d554-4979-bd92-893076640ffb');"""
        ),
    }

    for command, statement in funcs.items():
        try:
            postgres_client.cursor.execute(statement)
            postgres_client.connection.commit()
        except Exception as e:
            print(f"{command} was unsuccessful")
            print(e)
            postgres_client.connection.rollback()

    # Match has been found, i.e., person_id is not None
    person_id = "4d88cd35-5ee7-4419-a847-2818fdfeec88"
    postgres_client.insert_match_patient(
        patient_resource=patient_resource,
        person_id=person_id,
    )
    # Re-open connection for next test
    postgres_client.connection = postgres_client.get_connection()
    postgres_client.cursor = postgres_client.connection.cursor()

    # Extract all data
    postgres_client.cursor.execute(f"SELECT * from {postgres_client.patient_table}")
    postgres_client.connection.commit()
    data = postgres_client.cursor.fetchall()

    # Assert new patient record was added to patient table
    assert len(data) == 4

    # Assert new patient_id == id from patient resource
    assert data[-1][0] == patient_resource.get("id")

    # Assert person_id == inserted person_id
    assert data[-1][1] == person_id

    # Re-open connection for next test
    postgres_client.connection = postgres_client.get_connection()
    postgres_client.cursor = postgres_client.connection.cursor()

    postgres_client.cursor.execute(f"SELECT * from {postgres_client.person_table}")
    postgres_client.connection.commit()
    data = postgres_client.cursor.fetchall()

    # Assert record has not been added to person table
    assert len(data) == 3

    # Re-open connection for next test
    postgres_client.connection = postgres_client.get_connection()
    postgres_client.cursor = postgres_client.connection.cursor()

    # Match has not been found, i.e., new patient and person added, new person_id is
    # generated
    patient_resource = {
        "id": "4d88cd35-5ee7-4419-a847-2818fdfeec54",
        "address": "123 Main Street",
    }
    person_id = None
    postgres_client.insert_match_patient(
        patient_resource=patient_resource,
        person_id=person_id,
    )

    # Re-open connection for next test
    postgres_client.connection = postgres_client.get_connection()
    postgres_client.cursor = postgres_client.connection.cursor()

    postgres_client.cursor.execute(f"SELECT * from {postgres_client.patient_table}")
    postgres_client.connection.commit()
    data = postgres_client.cursor.fetchall()

    # Assert new patient record was added to patient table
    assert len(data) == 5
    assert data[-1][-1]["address"] == patient_resource["address"]

    # Re-open connection for next test
    postgres_client.connection = postgres_client.get_connection()
    postgres_client.cursor = postgres_client.connection.cursor()

    # Assert new patient record was added to person table with new person_id
    postgres_client.cursor.execute(f"SELECT * from {postgres_client.person_table}")
    data = postgres_client.cursor.fetchall()

    assert len(data) == 4
    assert data[-1][0] is not None

    _drop_tables(postgres_client)


def test_insert_person():
    postgres_client = _create_valid_mpi_client()
    postgres_client.connection = postgres_client.get_connection()
    postgres_client.cursor = postgres_client.connection.cursor()

    _create_tables(postgres_client)
    funcs = {
        "insert_person": (
            f"""INSERT INTO {postgres_client.person_table} (person_id) """
            + """VALUES ('ce02326f-7ecd-47ea-83eb-71e8d7c39131'),
             ('cb9dc379-38a9-4ed6-b3a7-a8a3db0e9e6c');"""
        ),
        "insert_external_source": (
            f"""INSERT INTO {postgres_client.external_source_table} """
            + "(external_source_key, external_source_name, "
            + "external_source_description) "
            + """VALUES ('f6a16ff7-4a31-11eb-be7b-8344edc8f36b',
            'Huerta Memorial Hospital', 'sample hospital for testing');"""
        ),
        "insert_external_id": (
            f"""INSERT INTO {postgres_client.external_person_id_table} """
            + " (external_id_key, person_id, external_person_id, "
            + "external_source_key) "
            + """VALUES ('2fdd0b8b-4a70-11eb-99fd-ad786a821574',
            'ce02326f-7ecd-47ea-83eb-71e8d7c39131', 
            'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
            'f6a16ff7-4a31-11eb-be7b-8344edc8f36b');"""
        ),
    }

    for command, statement in funcs.items():
        try:
            postgres_client.cursor.execute(statement)
            postgres_client.connection.commit()
        except Exception as e:
            print(f"{command} was unsuccessful")
            print(e)
            postgres_client.connection.rollback()

    # Test case 1: find matching person based on provided external
    # ID and external source
    supplied_external_id = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"
    supplied_external_source = "Huerta Memorial Hospital"
    expected_person_id = "ce02326f-7ecd-47ea-83eb-71e8d7c39131"

    match_result, found_person_id = postgres_client._insert_person(
        postgres_client.cursor, None, supplied_external_id, supplied_external_source
    )
    assert match_result
    assert found_person_id == expected_person_id

    # Test case 2: no external information supplied, no person_id
    # supplied; need a full insertion
    _, new_person_id = postgres_client._insert_person(postgres_client.cursor)

    # Verify that we added a new row to the person table
    assert new_person_id is not None
    query_data = [new_person_id]
    postgres_client.cursor.execute(
        f"SELECT person_id from {postgres_client.person_table} " "WHERE person_id = %s",
        query_data,
    )
    postgres_client.connection.commit()
    data = postgres_client.cursor.fetchall()
    assert len(data) == 1

    # Now check that we didn't add any null rows to the external info tables
    postgres_client.cursor.execute(
        f"SELECT * from {postgres_client.external_person_id_table} "
        "WHERE person_id = %s",
        query_data,
    )
    postgres_client.connection.commit()
    data = postgres_client.cursor.fetchall()
    assert data is None or len(data) == 0

    # Test case 3: no external information supplied, person_id supplied,
    # use existing person_id
    match_status, found_person_id = postgres_client._insert_person(
        postgres_client.cursor, new_person_id
    )
    assert match_status
    assert found_person_id == new_person_id

    # Check again that we didn't insert any garbage rows into external
    # tables, since we matched to a patient pulled from them
    postgres_client.cursor.execute(
        f"SELECT * from {postgres_client.external_person_id_table} "
        "WHERE person_id = %s",
        [found_person_id],
    )
    postgres_client.connection.commit()
    data = postgres_client.cursor.fetchall()
    assert data is None or len(data) == 0

    # Test case 4: supply external information but it doesn't match
    # any combination we've seen before, so create new person and
    # verify writing to external tables
    supplied_external_id = "a81bc81b-dead-4e5d-abff-90865d1e13b1"
    supplied_external_source = "Sirta Foundation"
    match_status, found_person_id = postgres_client._insert_person(
        postgres_client.cursor, None, supplied_external_id, supplied_external_source
    )
    assert not match_status

    # Verify new person row got created, bringing total up to 4
    postgres_client.cursor.execute(
        f"SELECT person_id from {postgres_client.person_table}", []
    )
    postgres_client.connection.commit()
    data = postgres_client.cursor.fetchall()
    assert data is not None and len(data) == 4

    # Check that there's a new row in the external sources table
    postgres_client.cursor.execute(
        f"SELECT * from {postgres_client.external_source_table} "
        "WHERE external_source_name = %s",
        [supplied_external_source],
    )
    postgres_client.connection.commit()
    data = postgres_client.cursor.fetchall()
    assert data is not None and len(data) == 1
    assert data[0][1] == supplied_external_source
    new_source_key = data[0][0]

    # Check that there's a new row in the external IDs table uniting
    # the new source with the new patient
    postgres_client.cursor.execute(
        f"SELECT external_source_key from {postgres_client.external_person_id_table} "
        "WHERE person_id = %s",
        [found_person_id],
    )
    postgres_client.connection.commit()
    data = postgres_client.cursor.fetchall()
    assert data is not None and len(data) == 1
    assert data[0][0] == new_source_key

    _drop_tables(postgres_client)
