import json
from pathlib import Path
from unittest import mock

import pytest
from app.main import app
from app.utils import CustomJSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient


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


# /process-message tests
@mock.patch("app.services.post_request")
@mock.patch("app.services.save_to_db")
def test_process_message_success(patched_post_request, patched_save_to_db):
    request = {
        "message_type": "ecr",
        "config_file_name": "sample-orchestration-config.json",
        "include_error_types": "errors",
        "message": '{"foo": "bar"}',
    }
    call_post_request = mock.Mock()
    call_post_request.status_code = 200
    call_post_request.json.return_value = {
        "response": {"FhirResource": {"foo": "bar"}},
        "bundle": {"foo": "bundle"},
    }
    save_to_db_response = CustomJSONResponse(
        content=jsonable_encoder(
            {
                "response": {"FhirResource": {"foo": "bar"}},
                "bundle": {"foo": "bundle"},
                "parsed_values": {"eicr_id": "foo"},
            }
        )
    )

    patched_post_request.return_value = call_post_request
    patched_save_to_db.return_value = save_to_db_response

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
        "message_type": "elr",
        "message": "foo",
        "config_file_name": "non_existent_schema.json",
        "include_error_types": "errors",
    }

    actual_response = client.post("/process-message", json=request)
    assert actual_response.status_code == 400
    assert actual_response.json() == {
        "message": "A config with the name 'non_existent_schema.json' could not be found.",  # noqa
        "processed_values": {},
    }


def test_process_message_input_validation_with_rr_data():
    request = {
        "message": "foo",
        "config_file_name": "sample-orchestration-config.json",
        "message_type": "elr",
        "include_error_types": "errors",
        "rr_data": "bar",
    }

    actual_response = client.post("/process-message", json=request)
    assert actual_response.status_code == 422


# /process tests
@mock.patch("app.services.post_request")
@mock.patch("app.services.save_to_db")
def test_process_success(patched_post_request, patched_save_to_db):
    with open(
        Path(__file__).parent.parent.parent.parent
        / "tests"
        / "assets"
        / "orchestration"
        / "eICR_RR_combo.zip",
        "rb",
    ) as f:
        form_data = {
            "message_type": "ecr",
            "config_file_name": "sample-orchestration-config.json",
            "include_error_types": "errors",
        }
        files = {"upload_file": ("file.zip", f)}

        call_post_request = mock.Mock()
        call_post_request.status_code = 200
        call_post_request.json.return_value = {
            "response": {
                "FhirResource": {"foo": "bar"},
            },
            "bundle": {"foo": "bundle"},
        }

        save_to_db_response = CustomJSONResponse(
            content=jsonable_encoder(
                {
                    "response": {"FhirResource": {"foo": "bar"}},
                    "bundle": {"foo": "bundle"},
                    "parsed_values": {"eicr_id": "foo"},
                }
            )
        )

        patched_post_request.return_value = call_post_request
        patched_save_to_db.return_value = save_to_db_response

        actual_response = client.post("/process", data=form_data, files=files)
        assert actual_response.status_code == 200


def test_process_with_empty_zip():
    with open(
        Path(__file__).parent.parent.parent.parent
        / "tests"
        / "assets"
        / "orchestration"
        / "empty.zip",
        "rb",
    ) as f:
        form_data = {
            "message_type": "ecr",
            "config_file_name": "sample-orchestration-config.json",
            "include_error_types": "errors",
        }
        files = {"upload_file": ("file.zip", f)}

        with pytest.raises(IndexError) as indexError:
            client.post("/process", data=form_data, files=files)
        error_message = str(indexError.value)
        assert "There is no eICR in this zip file." in error_message


def test_process_with_non_zip():
    with open(
        Path(__file__).parent.parent.parent.parent
        / "tests"
        / "assets"
        / "orchestration"
        / "CDA_eICR.xml",
        "rb",
    ) as f:
        form_data = {
            "message_type": "ecr",
            "config_file_name": "sample-orchestration-config.json",
            "include_error_types": "errors",
        }
        files = {"upload_file": ("file.xml", f)}

        actual_response = client.post("/process", data=form_data, files=files)
        assert actual_response.status_code == 422
        assert (
            actual_response.json()["detail"]
            == "Only .zip files are accepted at this time."
        )


def test_process_invalid_config():
    with open(
        Path(__file__).parent.parent.parent.parent
        / "tests"
        / "assets"
        / "orchestration"
        / "eICR_RR_combo.zip",
        "rb",
    ) as f:
        form_data = {
            "message_type": "ecr",
            "config_file_name": "non_existent_schema.json",
            "include_error_types": "errors",
        }
        files = {"upload_file": ("file.zip", f)}

        actual_response = client.post("/process", data=form_data, files=files)
        assert actual_response.status_code == 400
        assert actual_response.json() == {
            "message": "A config with the name 'non_existent_schema.json' could not be found.",  # noqa
            "processed_values": {},
        }
