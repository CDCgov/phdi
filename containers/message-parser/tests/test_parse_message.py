from fastapi.testclient import TestClient
import json
from pathlib import Path
from unittest import mock
from app.main import app


valid_tabulate_request = {
    "message_format": "fhir",
    "message_type": "ecr",
    "parsing_schema": {},
    "parsing_schema_name": "ecr.json",
    "fhir_converter_url": "my-fhir-converter-url",
    "credential_manager": "azure",
    "message": "my-message",
}

client = TestClient(app)

fhir_bundle_path = (
    Path(__file__).parent.parent.parent.parent
    / "tests"
    / "assets"
    / "patient_bundle.json"
)
with open(fhir_bundle_path, "r") as file:
    fhir_bundle = json.load(file)


def test_health_check():
    actual_response = client.get("/")
    assert actual_response.status_code == 200
    assert actual_response.json() == {"status": "OK"}


def test_parse_message_success_internal_schema():
    request = {
        "message_format": "fhir",
        "parsing_schema_name": "ecr.json",
        "message": fhir_bundle,
    }
    expected_response = {
        "message": "Parsing succeeded!",
        "parsed_values": {"first_name": "John ", "last_name": "doe"},
    }
    actual_response = client.post("/parse_message", json=request)
    assert actual_response.status_code == 200
    assert actual_response.json() == expected_response


def test_parse_message_success_external_schema():
    request = {
        "message_format": "fhir",
        "parsing_schema": {
            "first_name": "Bundle.entry.resource.where(resourceType = 'Patient').name.first().given.first()",
            "last_name": "Bundle.entry.resource.where(resourceType = 'Patient').name.first().family",
        },
        "message": fhir_bundle,
    }
    expected_response = {
        "message": "Parsing succeeded!",
        "parsed_values": {"first_name": "John ", "last_name": "doe"},
    }
    actual_response = client.post("/parse_message", json=request)
    assert actual_response.status_code == 200
    assert actual_response.json() == expected_response


@mock.patch("app.main.convert_to_fhir")
@mock.patch("app.main.get_credential_manager")
def test_parse_message_success_non_fhir(
    patched_get_credential_manager, patched_convert_to_fhir
):

    request = {
        "message_format": "hl7v2",
        "message_type": "elr",
        "parsing_schema_name": "ecr.json",
        "fhir_converter_url": "some-url",
        "credential_manager": "azure",
        "message": "some-hl7v2-elr-message",
    }

    patched_get_credential_manager.return_value = "some-credential-manager"
    convert_to_fhir_response = mock.Mock()
    convert_to_fhir_response.status_code = 200
    convert_to_fhir_response.json.return_value = {"FhirResource": fhir_bundle}
    patched_convert_to_fhir.return_value = convert_to_fhir_response
    expected_response = {
        "message": "Parsing succeeded!",
        "parsed_values": {"first_name": "John ", "last_name": "doe"},
    }

    actual_response = client.post("/parse_message", json=request)
    assert actual_response.status_code == 200
    assert actual_response.json() == expected_response
    patched_convert_to_fhir.assert_called_with(
        message="some-hl7v2-elr-message",
        message_type="elr",
        fhir_converter_url="some-url",
        credential_manager="some-credential-manager",
    )
    patched_get_credential_manager.assert_called_with(
        credential_manager="azure", location_url="some-url"
    )


def test_parse_message_non_fhir_missing_converter_url():

    request = {
        "message_format": "hl7v2",
        "message_type": "elr",
        "parsing_schema_name": "ecr.json",
        "message": "some-hl7v2-elr-message",
    }

    actual_response = client.post("/parse_message", json=request)
    assert actual_response.status_code == 400
    assert actual_response.json() == {
        "message": "The following values are required, but were not included in the request and could not be read from the environment. Please resubmit the request including these values or add them as environment variables to this service. missing values: fhir_converter_url.",
        "parsed_values": {},
    }


@mock.patch("app.main.convert_to_fhir")
def test_parse_message_success_non_fhir(patched_convert_to_fhir):

    request = {
        "message_format": "hl7v2",
        "message_type": "elr",
        "parsing_schema_name": "ecr.json",
        "fhir_converter_url": "some-url",
        "message": "some-hl7v2-elr-message",
    }

    convert_to_fhir_response = mock.Mock()
    convert_to_fhir_response.status_code = 400
    convert_to_fhir_response.text = "some error message returned by the FHIR converter"
    patched_convert_to_fhir.return_value = convert_to_fhir_response
    expected_response = {
        "message": f"Failed to convert to FHIR: {convert_to_fhir_response.text}",
        "parsed_values": {},
    }

    actual_response = client.post("/parse_message", json=request)
    assert actual_response.status_code == 400
    assert actual_response.json() == expected_response
    patched_convert_to_fhir.assert_called_with(
        message="some-hl7v2-elr-message",
        message_type="elr",
        fhir_converter_url="some-url",
        credential_manager=None,
    )

