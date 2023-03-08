from pathlib import Path
import json
from fastapi.testclient import TestClient
from app.main import app
import os


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

    response = client.get("/schemas/ecr.json")
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
