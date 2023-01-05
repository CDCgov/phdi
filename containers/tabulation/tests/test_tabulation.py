# flake8: noqa
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

valid_request = {
    "table_schema": {},
}

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
