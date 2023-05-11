from fastapi.testclient import TestClient
import json
from pathlib import Path
from unittest import mock
from app.main import app


client = TestClient(app)

fhir_bundle_path = (
    Path(__file__).parent.parent.parent.parent
    / "tests"
    / "assets"
    / "general"
    / "patient_bundle.json"
)

with open(fhir_bundle_path, "r") as file:
    fhir_bundle = json.load(file)

expected_successful_response = {
    "message": "Parsing succeeded!",
    "parsed_values": {"first_name": "John ", "last_name": "doe"},
}

expected_successful_response_full = {
    "message": "Parsing succeeded!",
    "parsed_values": {
        "patient_id": "some-uuid",
        "person_id": "",
        "last_name": "doe",
        "first_name": "John ",
        "rr_id": "",
        "status": "",
        "conditions": "",
        "eicr_id": "",
        "eicr_version_number": "",
        "authoring_datetime": "",
        "provider_id": "",
        "facility_id_number": "",
        "facility_name": "",
        "facility_type": "",
        "encounter_type": "",
        "encounter_start_date": "",
        "encounter_end_date": "",
        "active_problem_1": "",
        "active_problem_date_1": "",
        "active_problem_2": "",
        "active_problem_date_2": "",
        "active_problem_3": "",
        "active_problem_date_3": "",
        "active_problem_4": "",
        "active_problem_date_4": "",
        "active_problem_5": "",
        "active_problem_date_5": "",
        "reason_for_visit": "",
        "test_type_1": "",
        "test_type_code_1": "",
        "test_result_1": "",
        "test_result_interp_1": "",
        "specimen_type_1": "",
        "performing_lab_1": "",
        "specimen_collection_date_1": "",
        "result_date_1": "",
        "test_type_2": "",
        "test_type_code_2": "",
        "test_result_2": "",
        "test_result_interp_2": "",
        "specimen_type_2": "",
        "performing_lab_2": "",
        "specimen_collection_date_2": "",
        "result_date_2": "",
        "test_type_3": "",
        "test_type_code_3": "",
        "test_result_3": "",
        "test_result_interp_3": "",
        "specimen_type_3": "",
        "performing_lab_3": "",
        "specimen_collection_date_3": "",
        "result_date_3": "",
        "test_type_4": "",
        "test_type_code_4": "",
        "test_result_4": "",
        "test_result_interp_4": "",
        "specimen_type_4": "",
        "performing_lab_4": "",
        "specimen_collection_date_4": "",
        "result_date_4": "",
        "test_type_5": "",
        "test_type_code_5": "",
        "test_result_5": "",
        "test_result_interp_5": "",
        "specimen_type_5": "",
        "performing_lab_5": "",
        "specimen_collection_date_5": "",
        "result_date_5": "",
        "test_type_6": "",
        "test_type_code_6": "",
        "test_result_6": "",
        "test_result_interp_6": "",
        "specimen_type_6": "",
        "performing_lab_6": "",
        "specimen_collection_date_6": "",
        "result_date_6": "",
        "test_type_7": "",
        "test_type_code_7": "",
        "test_result_7": "",
        "test_result_interp_7": "",
        "specimen_type_7": "",
        "performing_lab_7": "",
        "specimen_collection_date_7": "",
        "result_date_7": "",
        "test_type_8": "",
        "test_type_code_8": "",
        "test_result_8": "",
        "test_result_interp_8": "",
        "specimen_type_8": "",
        "performing_lab_8": "",
        "specimen_collection_date_8": "",
        "result_date_8": "",
        "test_type_9": "",
        "test_type_code_9": "",
        "test_result_9": "",
        "test_result_interp_9": "",
        "specimen_type_9": "",
        "performing_lab_9": "",
        "specimen_collection_date_9": "",
        "result_date_9": "",
        "test_type_10": "",
        "test_type_code_10": "",
        "test_result_10": "",
        "test_result_interp_10": "",
        "specimen_type_10": "",
        "performing_lab_10": "",
        "specimen_collection_date_10": "",
        "result_date_10": "",
        "test_type_11": "",
        "test_type_code_11": "",
        "test_result_11": "",
        "test_result_interp_11": "",
        "specimen_type_11": "",
        "performing_lab_11": "",
        "specimen_collection_date_11": "",
        "result_date_11": "",
        "test_type_12": "",
        "test_type_code_12": "",
        "test_result_12": "",
        "test_result_interp_12": "",
        "specimen_type_12": "",
        "performing_lab_12": "",
        "specimen_collection_date_12": "",
        "result_date_12": "",
        "test_type_13": "",
        "test_type_code_13": "",
        "test_result_13": "",
        "test_result_interp_13": "",
        "specimen_type_13": "",
        "performing_lab_13": "",
        "specimen_collection_date_13": "",
        "result_date_13": "",
        "test_type_14": "",
        "test_type_code_14": "",
        "test_result_14": "",
        "test_result_interp_14": "",
        "specimen_type_14": "",
        "performing_lab_14": "",
        "specimen_collection_date_14": "",
        "result_date_14": "",
        "test_type_15": "",
        "test_type_code_15": "",
        "test_result_15": "",
        "test_result_interp_15": "",
        "specimen_type_15": "",
        "performing_lab_15": "",
        "specimen_collection_date_15": "",
        "result_date_15": "",
        "test_type_16": "",
        "test_type_code_16": "",
        "test_result_16": "",
        "test_result_interp_16": "",
        "specimen_type_16": "",
        "performing_lab_16": "",
        "specimen_collection_date_16": "",
        "result_date_16": "",
        "test_type_17": "",
        "test_type_code_17": "",
        "test_result_17": "",
        "test_result_interp_17": "",
        "specimen_type_17": "",
        "performing_lab_17": "",
        "specimen_collection_date_17": "",
        "result_date_17": "",
        "test_type_18": "",
        "test_type_code_18": "",
        "test_result_18": "",
        "test_result_interp_18": "",
        "specimen_type_18": "",
        "performing_lab_18": "",
        "specimen_collection_date_18": "",
        "result_date_18": "",
        "test_type_19": "",
        "test_type_code_19": "",
        "test_result_19": "",
        "test_result_interp_19": "",
        "specimen_type_19": "",
        "performing_lab_19": "",
        "specimen_collection_date_19": "",
        "result_date_19": "",
        "test_type_20": "",
        "test_type_code_20": "",
        "test_result_20": "",
        "test_result_interp_20": "",
        "specimen_type_20": "",
        "performing_lab_20": "",
        "specimen_collection_date_20": "",
        "result_date_20": "",
    },
}


def test_parse_message_success_internal_schema():
    test_request = {
        "message_format": "fhir",
        "parsing_schema_name": "ecr.json",
        "message": fhir_bundle,
    }

    actual_response = client.post("/parse_message", json=test_request)
    assert actual_response.status_code == 200
    assert actual_response.json() == expected_successful_response_full


def test_parse_message_success_external_schema():
    request = {
        "message_format": "fhir",
        "parsing_schema": {
            "first_name": "Bundle.entry.resource.where(resourceType = "
            "'Patient').name.first().given.first()",
            "last_name": "Bundle.entry.resource.where(resourceType = "
            "'Patient').name.first().family",
        },
        "message": fhir_bundle,
    }

    actual_response = client.post("/parse_message", json=request)
    assert actual_response.status_code == 200
    assert actual_response.json() == expected_successful_response


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

    actual_response = client.post("/parse_message", json=request)

    assert actual_response.status_code == 200
    assert actual_response.json() == expected_successful_response_full
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
        "message": "The following values are required, but were not included in the "
        "request and could not be read from the environment. Please resubmit the "
        "request including these values or add them as environment variables to this "
        "service. missing values: fhir_converter_url.",
        "parsed_values": {},
    }


@mock.patch("app.main.convert_to_fhir")
def test_parse_message_fhir_conversion_fail(patched_convert_to_fhir):
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


def test_parse_message_non_fhir_missing_message_type():
    request = {
        "message_format": "hl7v2",
        "parsing_schema_name": "ecr.json",
        "message": "some-hl7v2-elr-message",
    }

    actual_response = client.post("/parse_message", json=request)
    assert actual_response.status_code == 422
    assert (
        actual_response.json()["detail"][0]["msg"]
        == "When the message format is not FHIR then the message type must be included."
    )


def test_parse_message_internal_and_external_schema():
    request = {
        "message_format": "fhir",
        "parsing_schema": {"my-field": "FHIR.to.my.field"},
        "parsing_schema_name": "ecr.json",
        "message": "some-hl7v2-elr-message",
    }

    actual_response = client.post("/parse_message", json=request)
    assert actual_response.status_code == 422
    assert (
        actual_response.json()["detail"][0]["msg"]
        == "Values for both 'parsing_schema' and 'parsing_schema_name' have been "
        "provided. Only one of these values is permited."
    )


def test_parse_message_neither_internal_nor_external_schema():
    request = {
        "message_format": "fhir",
        "message": "some-hl7v2-elr-message",
    }

    actual_response = client.post("/parse_message", json=request)
    assert actual_response.status_code == 422
    assert (
        actual_response.json()["detail"][0]["msg"]
        == "Values for 'parsing_schema' and 'parsing_schema_name' have not been "
        "provided. One, but not both, of these values is required."
    )
