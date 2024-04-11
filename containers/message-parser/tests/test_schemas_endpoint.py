import json
import os
from pathlib import Path

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_list_loaded_schemas():
    response = client.get("/schemas")
    default_schemas = os.listdir(
        Path(__file__).parent.parent / "app" / "default_schemas"
    )
    assert response.status_code == 200
    assert response.json() == {
        "default_schemas": default_schemas,
        "custom_schemas": [],
    }


def test_get_specific_schema():
    test_schema_path = (
        Path(__file__).parent.parent / "app" / "default_schemas" / "test_schema.json"
    )
    with open(test_schema_path, "r") as file:
        test_schema = json.load(file)

    response = client.get("/schemas/test_schema.json")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Schema found!",
        "parsing_schema": test_schema,
    }


def test_schema_not_found():
    response = client.get("/schemas/some-schema-that-does-not-exist.json")
    assert response.status_code == 400
    assert response.json() == {
        "message": "A schema with the name 'some-schema-that-does-not-exist.json' "
        "could not be found.",
        "parsing_schema": {},
    }


def test_upload_schema():
    request_body = {
        "parsing_schema": {
            "my_field": {
                "fhir_path": "some-path",
                "data_type": "string",
                "nullable": True,
                "secondary_schema": {
                    "my_sub_field": {
                        "fhir_path": "some-path",
                        "data_type": "string",
                        "nullable": True,
                    }
                },
            }
        }
    }
    test_schema_name = "test_schema1.json"

    # Upload a new schema.
    response = client.put(
        f"/schemas/{test_schema_name}",
        json=request_body,
    )
    assert response.status_code == 201
    assert response.json() == {"message": "Schema uploaded successfully!"}

    response = client.put(
        "/schemas/test_schema1.json",
        json=request_body,
    )

    # Attempt to upload a schema with name that already exists.
    assert response.status_code == 400
    assert response.json() == {
        "message": f"A schema for the name '{test_schema_name}' already exists. "
        "To proceed submit a new request with a different schema name or set the "
        "'overwrite' field to 'true'."
    }
    request_body["overwrite"] = True
    response = client.put(
        "/schemas/test_schema1.json",
        json=request_body,
    )

    # Upload a schema with name that already exists and overwrite it.
    assert response.status_code == 200
    assert response.json() == {"message": "Schema updated successfully!"}

    # Delete the test schema to avoid conflicts with other tests.
    parsing_schema = (
        Path(__file__).parent.parent / "app" / "custom_schemas" / test_schema_name
    )
    parsing_schema.unlink()


def test_upload_schema_no_secondary():
    request_body = {
        "parsing_schema": {
            "my_field": {
                "fhir_path": "some-path",
                "data_type": "string",
                "nullable": True,
            }
        }
    }
    test_schema_name = "test_schema1.json"

    # Upload a new schema.
    response = client.put(
        f"/schemas/{test_schema_name}",
        json=request_body,
    )
    assert response.status_code == 201
    assert response.json() == {"message": "Schema uploaded successfully!"}

    response = client.put(
        "/schemas/test_schema1.json",
        json=request_body,
    )

    # Attempt to upload a schema with name that already exists.
    assert response.status_code == 400
    assert response.json() == {
        "message": f"A schema for the name '{test_schema_name}' already exists. "
        "To proceed submit a new request with a different schema name or set the "
        "'overwrite' field to 'true'."
    }
    request_body["overwrite"] = True
    response = client.put(
        "/schemas/test_schema1.json",
        json=request_body,
    )

    # Upload a schema with name that already exists and overwrite it.
    assert response.status_code == 200
    assert response.json() == {"message": "Schema updated successfully!"}

    # Delete the test schema to avoid conflicts with other tests.
    parsing_schema = (
        Path(__file__).parent.parent / "app" / "custom_schemas" / test_schema_name
    )
    parsing_schema.unlink()
