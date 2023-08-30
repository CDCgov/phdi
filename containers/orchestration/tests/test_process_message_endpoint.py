from fastapi.testclient import TestClient
import json
from pathlib import Path
from unittest import mock
from app.main import app


client = TestClient(app)

test_schema_path = (
    Path(__file__).parent.parent / "app" / "default_schemas" / "test_schema.json"
)

with open(test_schema_path, "r") as file:
    test_schema = json.load(file)

expected_successful_response = {
    "message": "Parsing succeeded!",
    "parsed_values": {"first_name": "John ", "last_name": "doe", "active_problems": []},
}


def test_process_message():
    request = {
        "processing_schema": test_schema,
        "message": {"foo": "bar"},
    }

    actual_response = client.post("/process", json=request)
    assert actual_response.status_code == 200


def test_process_message_failure():
    request = {
        "processing_schema": test_schema,
    }

    actual_response = client.post("/process", json=request)
    assert actual_response.status_code == 422
