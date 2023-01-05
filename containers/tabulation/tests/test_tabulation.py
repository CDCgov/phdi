# flake8: noqa
from fastapi.testclient import TestClient
import json
from unittest import mock
import pathlib
import copy
from app.main import app

client = TestClient(app)

valid_request = {
    "table_schema": {},
}

invalid_request = {"table_schema": {}}

valid_response = {}


def test_health_check():
    actual_response = client.get("/")
    assert actual_response.status_code == 200
    assert actual_response.json() == {"status": "OK"}


def test_validate_schema_pass():
    actual_response = client.post("/validate-schema", json=valid_request)
    assert actual_response.status_code == 200
    assert actual_response.json() == {
        "success": True,
        "isValid": True,
        "message": "Valid Schema",
    }


def test_validate_validation_fail():
    actual_response = client.post("/validate-schema", json=invalid_request)
    assert actual_response.status_code == 200
    assert actual_response.json() == {
        "success": True,
        "isValid": False,
        "message": "Invalid schema: Validation exception",
    }


valid_schema_path = (
    pathlib.Path(__file__).parent.parent.parent.parent
    / "tests"
    / "assets"
    / "valid_schema.json"
)
valid_schema = json.load(open(valid_schema_path))

valid_tabulate_request = {
    "output_type": "csv",
    "schema_name": "new_schema",
    "fhir_url": "http://localhost:8000/fhir/",
    "schema": valid_schema,
}


@mock.patch("app.main.tabulate")
def test_tabulate_endpoint_valid_request(patched_tabulate):
    valid_request = copy.deepcopy(valid_tabulate_request)
    actual_response = client.post("/tabulate", json=valid_request)
    valid_request["cred_manager"] = None
    valid_request["schema_"] = valid_tabulate_request["schema"]
    valid_request.pop("schema")
    assert actual_response.status_code == 200
    assert actual_response.json() == {}
    patched_tabulate.assert_called_with(**valid_request)


@mock.patch("app.main.tabulate")
def test_tabulate_endpoint_missing_schema(patched_tabulate):
    invalid_tabulate_request = copy.deepcopy(valid_tabulate_request)
    invalid_tabulate_request.pop("schema")
    actual_response = client.post("/tabulate", json=invalid_tabulate_request)
    assert actual_response.status_code == 422
    assert actual_response.json() == {
        "detail": [
            {
                "loc": ["body", "schema"],
                "msg": "field required",
                "type": "value_error.missing",
            }
        ]
    }


@mock.patch("app.main.tabulate")
def test_tabulate_endpoint_invalid_schema(patched_tabulate):
    invalid_tabulate_request = copy.deepcopy(valid_tabulate_request)
    invalid_tabulate_request["schema"] = {}
    actual_response = client.post("/tabulate", json=invalid_tabulate_request)
    assert actual_response.status_code == 422
    assert actual_response.json() == {
        "detail": [
            {
                "loc": ["body", "schema"],
                "msg": "Must provide a valid schema.",
                "type": "assertion_error",
            }
        ]
    }


@mock.patch("app.main.tabulate")
def test_tabulate_endpoint_missing_output_type(patched_tabulate):
    invalid_tabulate_request = copy.deepcopy(valid_tabulate_request)
    invalid_tabulate_request.pop("output_type")
    actual_response = client.post("/tabulate", json=invalid_tabulate_request)
    assert actual_response.status_code == 422
    assert actual_response.json() == {
        "detail": [
            {
                "loc": ["body", "output_type"],
                "msg": "field required",
                "type": "value_error.missing",
            }
        ]
    }


@mock.patch("app.main.tabulate")
def test_tabulate_endpoint_invalid_output_type(patched_tabulate):
    invalid_tabulate_request = copy.deepcopy(valid_tabulate_request)
    invalid_tabulate_request["output_type"] = "blah"
    actual_response = client.post("/tabulate", json=invalid_tabulate_request)
    assert actual_response.status_code == 422
    assert actual_response.json() == {
        "detail": [
            {
                "loc": ["body", "output_type"],
                "msg": "unexpected value; permitted: 'parquet', 'csv', 'sql'",
                "type": "value_error.const",
                "ctx": {"given": "blah", "permitted": ["parquet", "csv", "sql"]},
            }
        ]
    }


@mock.patch("app.main.tabulate")
def test_tabulate_endpoint_invalid_cred_manager(patched_tabulate):
    invalid_tabulate_request = copy.deepcopy(valid_tabulate_request)
    invalid_tabulate_request["cred_manager"] = "blah"
    actual_response = client.post("/tabulate", json=invalid_tabulate_request)
    assert actual_response.status_code == 422
    assert actual_response.json() == {
        "detail": [
            {
                "loc": ["body", "cred_manager"],
                "msg": "unexpected value; permitted: 'azure', 'gcp'",
                "type": "value_error.const",
                "ctx": {"given": "blah", "permitted": ["azure", "gcp"]},
            }
        ]
    }
