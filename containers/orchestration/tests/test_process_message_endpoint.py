from fastapi.testclient import TestClient
import json
from pathlib import Path
from unittest import mock
import pytest

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


# /process-message tests
@mock.patch("app.services.post_request")
def test_process_message_success(patched_post_request):
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

    actual_response = client.post("/process-message", json=request)
    assert actual_response.status_code == 200


def test_process_message_input_validation():
    request = {
        "processing_config": test_config,
    }

    actual_response = client.post("/process-message", json=request)
    assert actual_response.status_code == 422


def test_process_message_input_validation_with_rr_data():
    request = {
        "message": "foo",
        "message_type": "elr",
        "include_error_types": "errors",
        "rr_data": "bar",
    }

    actual_response = client.post("/process-message", json=request)
    assert actual_response.status_code == 422


# /process tests
@mock.patch("app.services.post_request")
def test_process_success(patched_post_request):
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
            "include_error_types": "errors",
        }
        files = {"upload_file": ("file.zip", f)}

        call_post_request = mock.Mock()
        call_post_request.status_code = 200
        call_post_request.json.return_value = {
            "response": {"FhirResource": {"foo": "bar"}},
            "bundle": {"foo": "bundle"},
        }
        patched_post_request.return_value = call_post_request

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
            "include_error_types": "errors",
        }
        files = {"upload_file": ("file.xml", f)}

        actual_response = client.post("/process", data=form_data, files=files)
        assert actual_response.status_code == 422
        assert (
            actual_response.json()["detail"]
            == "Only .zip files are accepted at this time."
        )
