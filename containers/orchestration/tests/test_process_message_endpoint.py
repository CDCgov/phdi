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


@mock.patch("app.main.call_message_parser")
@mock.patch("app.main.call_ingestion")
@mock.patch("app.main.call_fhir_converter")
@mock.patch("app.main.call_validation")
def test_process_message(
    patched_call_validation,
    patched_call_fhir_converter,
    patched_call_ingestion,
    patched_call_message_parser,
):
    request = {
        "message_type": "ecr",
        "include_error_types": "errors",
        "message": '{"foo": "bar"}',
    }
    call_validation_response = mock.Mock()
    call_validation_response.status_code = 200
    call_validation_response.json.return_value = {"FhirResource": {"foo": "bar"}}
    patched_call_validation.return_value = call_validation_response

    call_fhir_converter_response = mock.Mock()
    call_fhir_converter_response.status_code = 200
    call_fhir_converter_response.json.return_value = {"FhirResource": fhir_bundle}
    patched_call_fhir_converter.return_value = call_fhir_converter_response

    call_ingestion_response = mock.Mock()
    call_ingestion_response.status_code = 200
    call_ingestion_response.json.return_value = {
        "FhirResource": fhir_bundle,
        "bundle": fhir_bundle,
    }
    patched_call_ingestion.return_value = call_ingestion_response

    call_message_parser_response = mock.Mock()
    call_message_parser_response.status_code = 200
    call_message_parser_response.json.return_value = {
        "FhirResource": fhir_bundle,
        "bundle": fhir_bundle,
    }
    patched_call_message_parser.return_value = call_message_parser_response

    actual_response = client.post("/process", json=request)
    assert actual_response.status_code == 200

    patched_call_validation.assert_called_with(
        input=request,
        response=request,
        step=test_config["steps"][0],
    )

    patched_call_fhir_converter.assert_called_with(
        input=request,
        response=patched_call_validation.return_value,
        step=test_config["steps"][1],
    )

    expected_call_count = 4
    assert patched_call_ingestion.call_count == expected_call_count, (
        f"Expected {expected_call_count} calls, but got "
        + f"{patched_call_ingestion.call_count} calls."
    )

    expected_call_count = 1
    assert patched_call_message_parser.call_count == expected_call_count, (
        f"Expected {expected_call_count} calls, but got "
        + f"{patched_call_message_parser.call_count} calls."
    )


def test_process_message_failure():
    request = {
        "processing_config": test_config,
    }

    actual_response = client.post("/process", json=request)
    assert actual_response.status_code == 422
