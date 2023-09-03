from fastapi.testclient import TestClient
import json
from pathlib import Path
from app.main import app


client = TestClient(app)

test_config_path = (
    Path(__file__).parent.parent / "app" / "default_configs" / "test_config.json"
)

with open(test_config_path, "r") as file:
    test_config = json.load(file)

expected_successful_response = {
    "message": "Parsing succeeded!",
    "parsed_values": {"first_name": "John ", "last_name": "doe", "active_problems": []},
}


def test_process_message():
    request = {
        "processing_config": test_config,
        "message": {"foo": "bar"},
    }

    actual_response = client.post("/process", json=request)
    assert actual_response.status_code == 200


def test_process_message_failure():
    request = {
        "processing_config": test_config,
    }

    actual_response = client.post("/process", json=request)
    assert actual_response.status_code == 422
