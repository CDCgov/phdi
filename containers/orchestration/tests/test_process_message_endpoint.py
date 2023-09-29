from fastapi.testclient import TestClient
import json
from pathlib import Path
from unittest import mock

from app.main import app


client = TestClient(app)

test_config_path = (
    Path(__file__).parent.parent
    / "app"
    / "default_configs"
    / "sample-orchestration-config.json"
)

fhir_bundle_path = (
    Path(__file__).parent.parent.parent.parent
    / "tests"
    / "assets"
    / "general"
    / "patient_bundle.json"
)

with open(fhir_bundle_path, "r") as file:
    fhir_bundle = json.load(file)

with open(test_config_path, "r") as file:
    test_config = json.load(file)

expected_successful_response = {
    "message": "Processing succeeded!",
    "processed_values": {
        "first_name": "John ",
        "last_name": "doe",
        "active_problems": [],
    },
}


@mock.patch("app.services.post_request")
def test_process_message(patched_post_request):
    request = {
        "message_type": "ecr",
        "include_error_types": "errors",
        "message": '{"foo": "bar"}',
    }
    call_post_request = mock.Mock()
    call_post_request.status_code = 200
    call_post_request.json.return_value = {
        "response": {"FhirResource": {"foo": "bar"}},
        "bundle": {"foo": "bundle"},
    }
    patched_post_request.return_value = call_post_request

    actual_response = client.post("/process", json=request)
    assert actual_response.status_code == 200


def test_process_message_failure():
    request = {
        "processing_config": test_config,
    }

    actual_response = client.post("/process", json=request)
    assert actual_response.status_code == 400

