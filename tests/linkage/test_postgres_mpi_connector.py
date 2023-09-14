from phdi.linkage.mpi.postgres import DIBBsConnectorClient
import pathlib
import pytest
import json
import copy


def test_postgres_connection():
    postgres_client = create_valid_mpi_client()
    postgres_client.connection = postgres_client.get_connection()
    postgres_client.cursor = postgres_client.connection.cursor()

    assert postgres_client.connection is not None
    postgres_client.cursor.close()
    postgres_client.connection.close()


def test_generate_block_query():
    postgres_client = create_valid_mpi_client()
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
    postgres_client = create_valid_mpi_client()

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
    # Create test table and insert data
    funcs = {
        "drop tables": (
            f"""
        DROP TABLE IF EXISTS {postgres_client.patient_table};
        DROP TABLE IF EXISTS {postgres_client.person_table};
        """
        ),
        "create": (
            """
            BEGIN;

            CREATE EXTENSION IF NOT EXISTS "uuid-ossp";"""
            + f"CREATE TABLE IF NOT EXISTS {postgres_client.patient_table} "
            + "(patient_id UUID DEFAULT uuid_generate_v4 (), person_id UUID, "
            + "patient_resource JSONB);"
        ),
        "insert": (
            f"""INSERT INTO {postgres_client.patient_table}
             (person_id, patient_resource) """
            + f"""VALUES ('4d88cd35-5ee7-4419-a847-2818fdfeec38',
            '{json.dumps(patient_resource)}');"""
        ),
    }
    postgres_client.connection = postgres_client.get_connection()
    postgres_client.cursor = postgres_client.connection.cursor()

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
    assert 1 == 2

    # Clean up
    postgres_client.connection = postgres_client.get_connection()
    postgres_client.cursor = postgres_client.connection.cursor()
    postgres_client.cursor.execute(
        f"DROP TABLE IF EXISTS {postgres_client.patient_table}"
    )
    postgres_client.connection.commit()
    postgres_client.connection.close()


def test_dibbs_blocking():
    postgres_client = create_valid_mpi_client()

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

    # Create test table and insert data
    funcs = {
        "drop tables": (
            f"""
        DROP TABLE IF EXISTS {postgres_client.patient_table};
        DROP TABLE IF EXISTS {postgres_client.person_table};
        """
        ),
        "create": (
            """
            BEGIN;

            CREATE EXTENSION IF NOT EXISTS "uuid-ossp";"""
            + f"CREATE TABLE IF NOT EXISTS {postgres_client.patient_table} "
            + "(patient_id UUID DEFAULT uuid_generate_v4 (), person_id UUID, "
            + "patient_resource JSONB);"
        ),
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
    postgres_client.connection = postgres_client.get_connection()
    postgres_client.cursor = postgres_client.connection.cursor()

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


def test_insert_match_patient():
    postgres_client = create_valid_mpi_client()
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

    # Generate test tables
    # Create test table and insert data
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
            + "(person_id UUID DEFAULT uuid_generate_v4 (), "
            + "external_person_id VARCHAR(100));"
        ),
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
            f"""INSERT INTO {postgres_client.person_table} (person_id, """
            + "external_person_id) "
            + """VALUES ('ce02326f-7ecd-47ea-83eb-71e8d7c39131',
            '4d88cd35-5ee7-4419-a847-2818fdfeec38'),
             ('cb9dc379-38a9-4ed6-b3a7-a8a3db0e9e6c',
             '4d88cd35-5ee7-4419-a847-2818fdfeec39'),
             ('c2477ae3-d554-4979-bd92-893076640ffb',
             '4d88cd35-5ee7-4419-a847-2818fdfeec40');"""
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

    # Clean up
    postgres_client.connection = postgres_client.get_connection()
    postgres_client.cursor = postgres_client.connection.cursor()
    postgres_client.cursor.execute(
        f"DROP TABLE IF EXISTS {postgres_client.patient_table}"
    )
    postgres_client.connection.commit()
    postgres_client.cursor.execute(
        f"DROP TABLE IF EXISTS {postgres_client.person_table}"
    )
    postgres_client.connection.commit()
    postgres_client.cursor.close()
    postgres_client.connection.close()


def create_valid_mpi_client():
    return DIBBsConnectorClient(
        database="testdb",
        user="postgres",
        password="pw",
        host="localhost",
        port="5432",
        patient_table="test_patient_mpi",
        person_table="test_person_mpi",
    )


def test_insert_person():
    postgres_client = create_valid_mpi_client()
    postgres_client.connection = postgres_client.get_connection()
    postgres_client.cursor = postgres_client.connection.cursor()

    # Generate test tables
    # Create test table and insert data
    funcs = {
        "drop tables": (
            f"""
        DROP TABLE IF EXISTS {postgres_client.person_table};
        """
        ),
        "create_person": (
            """
            BEGIN;

            CREATE EXTENSION IF NOT EXISTS "uuid-ossp";"""
            + f"CREATE TABLE IF NOT EXISTS {postgres_client.person_table} "
            + "(person_id UUID DEFAULT uuid_generate_v4 (), "
            + "external_person_id VARCHAR(100));"
        ),
        "insert_person": (
            f"""INSERT INTO {postgres_client.person_table} (person_id, """
            + "external_person_id) "
            + """VALUES ('ce02326f-7ecd-47ea-83eb-71e8d7c39131',
            '4d88cd35-5ee7-4419-a847-2818fdfeec38'),
             ('cb9dc379-38a9-4ed6-b3a7-a8a3db0e9e6c',
             'NULL');"""
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

    # Find the person based upon the external person id
    external_person_id_test = "4d88cd35-5ee7-4419-a847-2818fdfeec38"
    expected_person_id = "ce02326f-7ecd-47ea-83eb-71e8d7c39131"

    # send in null person_id and external_person_id populated and get back a person_id
    actual_result, actual_person_id = postgres_client._insert_person(
        postgres_client.cursor, None, external_person_id_test
    )

    # Assert existing person_id from MPI

    assert actual_result
    assert actual_person_id == expected_person_id

    # Now we will insert a new person with a null external id
    actual_result, new_person_id = postgres_client._insert_person(
        postgres_client.cursor, None, None
    )
    query_data = [new_person_id]
    postgres_client.cursor.execute(
        f"SELECT * from {postgres_client.person_table} " "WHERE person_id = %s",
        query_data,
    )
    postgres_client.connection.commit()
    data = postgres_client.cursor.fetchall()

    # Assert record was added to the table
    assert len(data) == 1
    assert new_person_id is not None

    # Send in a valid person id and a new external person id
    # for a person record where the external person id is null
    # should update the person record with the new external person id
    valid_person_id = "cb9dc379-38a9-4ed6-b3a7-a8a3db0e9e6c"
    new_external_person_id = "bbbbbbbb-38a9-4ed6-b3a7-a8a3db0e9e6c"
    update_matched, update_person_id = postgres_client._insert_person(
        postgres_client.cursor, valid_person_id, new_external_person_id
    )

    query_data = [valid_person_id]

    postgres_client.cursor.execute(
        f"SELECT external_person_id from {postgres_client.person_table} "
        "WHERE person_id = %s",
        query_data,
    )
    postgres_client.connection.commit()
    data = postgres_client.cursor.fetchall()[0][0]

    # Assert record was updated in table
    assert update_matched
    assert update_person_id == valid_person_id
    assert data == new_external_person_id

    # Clean up
    postgres_client.connection = postgres_client.get_connection()
    postgres_client.cursor = postgres_client.connection.cursor()
    postgres_client.cursor.execute(
        f"DROP TABLE IF EXISTS {postgres_client.person_table}"
    )
    postgres_client.connection.commit()
    postgres_client.cursor.close()
    postgres_client.connection.close()
