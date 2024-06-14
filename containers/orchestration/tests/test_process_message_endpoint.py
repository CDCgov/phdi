import json
from pathlib import Path
from unittest import mock

import pytest
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

test_config_path = (
    Path(__file__).parent.parent
    / "app"
    / "default_configs"
    / "sample-orchestration-config.json"
)

fhir_bundle_path = Path(__file__).parent / "assets" / "patient_bundle.json"

with open(fhir_bundle_path, "r") as file:
    fhir_bundle = json.load(file)

with open(test_config_path, "r") as file:
    test_config = json.load(file)


def mock_headers_get(key, default=None):
    headers = {
        "content-type": "application/json",
    }
    return headers.get(key, default)


"""
Note: The tests in this file all begin with realistic data inputs,
but do not compute intermediary updates to that data in the mock
steps for each service. E.g. an actual HL7 message may be provided
as one test's initial input, but the convert-to-fhir mock doesn't
contain the actual FHIR converted bundle, the ingestion mock doesn't
contain the standardized FHIR bundle, etc. These tests verify
expected data flow, and the integration tests verify how that flow
manifests on real data in each step.
"""


# /process-message tests
@mock.patch("app.services.post_request")
def test_process_message_success(patched_post_request):
    message = open(Path(__file__).parent / "assets" / "hl7_with_msh_3_set.hl7").read()
    request = {
        "message_type": "elr",
        "data_type": "hl7",
        "config_file_name": "sample-orchestration-config.json",
        "message": message,
    }
    # Need a mocked return value for each of the called services,
    # which we can use a side_effect iterator to sequentially return
    validation_post_request = mock.Mock()
    validation_post_request.status_code = 200
    validation_post_request.json.return_value = {
        "validation_results": [],
        "message_valid": True,
    }
    conversion_post_request = mock.Mock()
    conversion_post_request.status_code = 200
    conversion_post_request.json.return_value = {
        "response": {
            "FhirResource": {
                "bundle": {
                    "bundle_type": "batch",
                    "placeholder_id": "abcdefg",
                    "entry": [],
                }
            }
        },
        "bundle": {
            "converted_msg_placeholder_key": "placeholder_bundle",
            "entry": [{"resource": {"id": "foo"}}],
        },
    }
    ingestion_post_request = mock.Mock()
    ingestion_post_request.status_code = 200
    ingestion_post_request.json.return_value = {
        "bundle": {
            "bundle_type": "batch",
            "placeholder_id": "abcdefg",
            "entry": [{"resource": {"id": "foo"}}],
        }
    }
    message_parser_post_request = mock.Mock()
    message_parser_post_request.status_code = 200
    message_parser_post_request.json.return_value = {
        "parsed_values": {"eicr_id": "placeholder_id"}
    }

    save_bundle_post_request = mock.Mock()
    save_bundle_post_request.status_code = 200
    save_bundle_post_request.headers = {"content-type": "application/json"}
    save_bundle_post_request.json.return_value = {
        "message": "Success. Saved FHIR Bundle to S3: placeholder_id"
    }

    patched_post_request.side_effect = [
        validation_post_request,
        conversion_post_request,
        ingestion_post_request,
        ingestion_post_request,
        ingestion_post_request,
        message_parser_post_request,
        save_bundle_post_request,
    ]

    actual_response = client.post("/process-message", json=request)
    assert actual_response.status_code == 200


@mock.patch("app.services.post_request")
def test_process_message_fhir_data(patched_post_request):
    request = {
        "message_type": "fhir",
        "data_type": "fhir",
        "config_file_name": "sample-fhir-test-config.json",
        "message": {"foo": "bar"},
    }
    ingestion_post_request = mock.Mock()
    ingestion_post_request.status_code = 200
    ingestion_post_request.headers = {"content-type": "application/json"}
    ingestion_post_request.json.return_value = {
        "bundle": {"bundle_type": "batch", "placeholder_id": "abcdefg", "entry": []}
    }
    message_parser_post_request = mock.Mock()
    message_parser_post_request.status_code = 200
    message_parser_post_request.headers = {"content-type": "application/json"}
    message_parser_post_request.json.return_value = {
        "parsed_values": {"placeholder_key": "placeholder_value"}
    }
    patched_post_request.side_effect = [
        ingestion_post_request,
        ingestion_post_request,
        ingestion_post_request,
        message_parser_post_request,
    ]
    actual_response = client.post("/process-message", json=request)
    assert actual_response.status_code == 200


def test_process_message_input_validation():
    request = {
        "processing_config": test_config,
    }

    actual_response = client.post("/process-message", json=request)
    assert actual_response.status_code == 422


def test_process_message_invalid_config():
    request = {
        "message_type": "ecr",
        "data_type": "ecr",
        "message": "foo",
        "config_file_name": "non_existent_schema.json",
    }

    actual_response = client.post("/process-message", json=request)
    assert actual_response.status_code == 400
    assert actual_response.json() == {
        "message": "A config with the name 'non_existent_schema.json' could not be found.",  # noqa
        "processed_values": {},
    }


def test_process_message_mismatched_data_types():
    request = {
        "message_type": "ecr",
        "data_type": "fhir",
        "message": "foo",
        "config_file_name": "sample-orchestration-config.json",
    }
    actual_response = client.post("/process-message", json=request)
    assert actual_response.status_code == 422
    assert (
        actual_response.json()["detail"][0]["msg"]
        == "For an eCR message, `data_type` must be either `ecr` or `zip`."
    )

    request["message_type"] = "fhir"
    request["data_type"] = "zip"
    actual_response = client.post("/process-message", json=request)
    assert actual_response.status_code == 422
    assert (
        actual_response.json()["detail"][0]["msg"]
        == "`data_type` and `message_type` parameters must both be `fhir` in "
        "order to process a FHIR bundle."
    )


def test_process_message_invalid_fhir():
    request = {
        "message_type": "fhir",
        "data_type": "fhir",
        "message": json.dumps("foo"),
        "config_file_name": "sample-orchestration-config.json",
    }
    actual_response = client.post("/process-message", json=request)
    assert actual_response.status_code == 422
    assert (
        actual_response.json()["detail"][0]["msg"]
        == "A `data_type` of FHIR requires the input message "
        "to be a valid dictionary."
    )


def test_process_message_input_validation_with_rr_data():
    request = {
        "message": "foo",
        "data_type": "elr",
        "config_file_name": "sample-orchestration-config.json",
        "message_type": "elr",
        "rr_data": "bar",
    }

    actual_response = client.post("/process-message", json=request)
    assert actual_response.status_code == 422


# # /process tests
@mock.patch("app.services.post_request")
def test_process_success(patched_post_request):
    with open(
        Path(__file__).parent / "assets" / "eICR_RR_combo.zip",
        "rb",
    ) as f:
        form_data = {
            "message_type": "ecr",
            "data_type": "zip",
            "config_file_name": "sample-orchestration-config.json",
        }
        files = {"upload_file": ("file.zip", f)}

        call_post_request = mock.Mock()
        call_post_request.status_code = 200
        call_post_request.json.return_value = {
            "response": {
                "FhirResource": {"foo": "bar"},
            },
            "bundle": {"entry": [{"resource": {"id": "foo"}}]},
        }
        validation_post_request = mock.Mock()
        validation_post_request.status_code = 200
        validation_post_request.json.return_value = {
            "validation_results": [],
            "message_valid": True,
        }
        conversion_post_request = mock.Mock()
        conversion_post_request.status_code = 200
        conversion_post_request.json.return_value = {
            "response": {
                "FhirResource": {
                    "bundle": {
                        "bundle_type": "batch",
                        "placeholder_id": "abcdefg",
                        "entry": [],
                    }
                }
            }
        }
        ingestion_post_request = mock.Mock()
        ingestion_post_request.status_code = 200
        ingestion_post_request.json.return_value = {
            "bundle": {
                "bundle_type": "batch",
                "placeholder_id": "abcdefg",
                "entry": [{"resource": {"id": "foo"}}],
            }
        }
        message_parser_post_request = mock.Mock()
        message_parser_post_request.status_code = 200
        message_parser_post_request.json.return_value = {
            "parsed_values": {"eicr_id": "placeholder_id"}
        }
        save_bundle_post_request = mock.Mock()
        save_bundle_post_request.status_code = 200
        save_bundle_post_request.headers = {"content-type": "application/json"}
        save_bundle_post_request.json.return_value = {
            "message": "Success. Saved FHIR Bundle to S3: placeholder_id"
        }

        patched_post_request.side_effect = [
            validation_post_request,
            conversion_post_request,
            ingestion_post_request,
            ingestion_post_request,
            ingestion_post_request,
            message_parser_post_request,
            save_bundle_post_request,
        ]

        actual_response = client.post("/process", data=form_data, files=files)
        assert actual_response.status_code == 200


def test_process_with_empty_zip():
    with open(
        Path(__file__).parent / "assets" / "empty.zip",
        "rb",
    ) as f:
        form_data = {
            "message_type": "ecr",
            "data_type": "zip",
            "config_file_name": "sample-orchestration-config.json",
        }
        files = {"upload_file": ("file.zip", f)}

        with pytest.raises(BaseException) as indexError:
            client.post("/process", data=form_data, files=files)
        error_message = str(indexError)
        assert "There is no eICR in this zip file." in error_message


def test_process_invalid_config():
    with open(
        Path(__file__).parent / "assets" / "eICR_RR_combo.zip",
        "rb",
    ) as f:
        form_data = {
            "message_type": "ecr",
            "data_type": "zip",
            "config_file_name": "non_existent_schema.json",
        }
        files = {"upload_file": ("file.zip", f)}

        actual_response = client.post("/process", data=form_data, files=files)
        assert actual_response.status_code == 400
        assert actual_response.json() == {
            "message": "A config with the name 'non_existent_schema.json' could not be found.",  # noqa
            "processed_values": {},
        }
