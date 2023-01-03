# flake8: noqa
from unittest import mock
from fastapi.testclient import TestClient
from pathlib import Path
import json


from main import api

client = TestClient(api)

schema_text = json.loads(Path("./valid_schema.json").read_text())

valid_request = {"schema": schema_text}

invalid_request = {"schema": {}}

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


def test_tabulate():
    actual_response = client.post("/tabulate", json=valid_request)
    assert actual_response.status_code == 200
    assert actual_response.json() == valid_response
