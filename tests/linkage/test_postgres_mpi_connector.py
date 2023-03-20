from phdi.linkage.postgres import PostgresConnectorClient
import pathlib
import pytest
import json


def test_postgres_connection():
    postgres_client = PostgresConnectorClient(
        database="testdb",
        user="postgres",
        password="pw",
        host="localhost",
        port="5432",
        patient_table="test_patient_mpi",
        person_table="test_person_mpi",
    )
    assert postgres_client.connection is not None

    # Test with failed connection, e.g., bad password
    with pytest.raises(ValueError) as e:
        postgres_client = PostgresConnectorClient(
            database="testdb",
            user="postgres",
            password="bad password",
            host="localhost",
            port="5432",
            patient_table="test_patient_mpi",
            person_table="test_person_mpi",
        )
        assert """connection to server at "localhost" (::1), port 5432 failed: FATAL: 
        password authentication failed for user "postgres" """ in str(
            e.value
        )


def test_generate_block_query():
    postgres_client = PostgresConnectorClient(
        database="testdb",
        user="postgres",
        password="pw",
        host="localhost",
        port="5432",
        patient_table="test_patient_mpi",
        person_table="test_person_mpi",
    )
    table_name = "test_patient_mpi"
    block_data = {"ZIP": "90120-1001", "LAST4": "GONZ"}
    expected_query = (
        "SELECT * FROM test_patient_mpi WHERE patient_resource->>'ZIP' = '90120-1001' "
        + "AND patient_resource->>'LAST4' = 'GONZ';"
    )

    generated_query = postgres_client._generate_block_query(table_name, block_data)

    assert expected_query == generated_query


def test_block_data():
    postgres_client = PostgresConnectorClient(
        database="testdb",
        user="postgres",
        password="pw",
        host="localhost",
        port="5432",
        patient_table="test_patient_mpi",
        person_table="test_person_mpi",
    )
    table_name = "test_patient_mpi"
    block_data = {}

    # Test for invalue block data
    with pytest.raises(ValueError) as e:
        blocked_data = postgres_client.block_data(block_data)
        assert "`block_data` cannot be empty." in str(e.value)

    block_data = {"LAST4": "GONZ"}

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
            + """VALUES ('4d88cd35-5ee7-4419-a847-2818fdfeec38',
            '{"FIRST4":"JOHN","LAST4":"SMIT","ZIP":"90120-1001"}'),
            ('4d88cd35-5ee7-4419-a847-2818fdfeec39',
            '{"FIRST4":"JOSE","LAST4":"GONZ","ZIP":"90120-1001"}'),
            ('4d88cd35-5ee7-4419-a847-2818fdfeec40',
            '{"FIRST4":"MARI","LAST4":"GONZ","ZIP":"90120-1001"}');"""
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

    blocked_data = postgres_client.block_data(block_data)

    # Assert that all returned data matches blocking criterion
    for row in blocked_data[1:]:
        assert row[-2] == block_data["LAST4"]

    # Assert returned data are LoL
    assert type(blocked_data[0]) is list

    # Clean up
    postgres_client.cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    postgres_client.connection.commit()
    postgres_client.connection.close()


def test_upsert_match_patient():
    postgres_client = PostgresConnectorClient(
        database="testdb",
        user="postgres",
        password="pw",
        host="localhost",
        port="5432",
        patient_table="test_patient_mpi",
        person_table="test_person_mpi",
    )

    raw_bundle = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "tests"
            / "assets"
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
    postgres_client.upsert_match_patient(
        patient_resource=patient_resource,
        person_id=person_id,
    )

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

    postgres_client.cursor.execute(f"SELECT * from {postgres_client.person_table}")
    postgres_client.connection.commit()
    data = postgres_client.cursor.fetchall()

    # Assert record has been added to person table
    assert len(data) == 4

    # Assert new external_person_id == id from patient resource
    assert data[-1][1] == patient_resource.get("id")

    # Assert person_id == inserted person_id
    assert data[-1][0] == person_id

    # Clean up

    # Match has not been found, i.e., new patient and person added, new person_id is
    # generated
    patient_resource = {
        "id": "4d88cd35-5ee7-4419-a847-2818fdfeec54",
        "address": "123 Main Street",
    }
    person_id = None
    postgres_client.upsert_match_patient(
        patient_resource=patient_resource,
        person_id=person_id,
    )

    postgres_client.cursor.execute(f"SELECT * from {postgres_client.patient_table}")
    postgres_client.connection.commit()
    data = postgres_client.cursor.fetchall()

    # Assert new patient record was added to patient table
    assert len(data) == 5
    assert data[-1][-1]["address"] == patient_resource["address"]

    # Assert new patient record was added to person table with new person_id
    postgres_client.cursor.execute(f"SELECT * from {postgres_client.person_table}")
    postgres_client.connection.commit()
    data = postgres_client.cursor.fetchall()

    assert len(data) == 5
    assert data[-1][-1] == patient_resource["id"]
    assert data[-1][0] is not None

    # Clean up
    postgres_client.cursor.execute(
        f"DROP TABLE IF EXISTS {postgres_client.patient_table}"
    )
    postgres_client.connection.commit()
    postgres_client.cursor.execute(
        f"DROP TABLE IF EXISTS {postgres_client.person_table}"
    )
    postgres_client.connection.commit()
    postgres_client.connection.close()
