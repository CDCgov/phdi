# flake8: noqa
from unittest import mock
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

valid_request = {
    "table_schema": {},
}

valid_response = {}


def test_health_check():
    actual_response = client.get("/")
    assert actual_response.status_code == 200
    assert actual_response.json() == {"status": "OK"}


def test_tabulate():
    actual_response = client.post("/tabulate", json=valid_request)
    assert actual_response.status_code == 200
    assert actual_response.json() == valid_response
