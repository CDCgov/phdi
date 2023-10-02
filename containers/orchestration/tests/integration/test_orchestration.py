import httpx
import pytest
from pathlib import Path


ORCHESTRATION_URL = "http://0.0.0.0:8080"
PROCESS_ENDPOINT = ORCHESTRATION_URL + "/process"


@pytest.mark.integration
def test_health_check(setup):
    health_check_response = httpx.get(ORCHESTRATION_URL)
    assert health_check_response.status_code == 200


@pytest.mark.integration
def test_process_endpoint_with_message(setup):
    message = open(
        Path(__file__).parent.parent.parent.parent.parent
        / "tests"
        / "assets"
        / "orchestration"
        / "CDA_eICR.xml"
    ).read()
    request = {
        "message_type": "ecr",
        "include_error_types": "errors",
        "message": message,
    }
    orchestration_response = httpx.post(PROCESS_ENDPOINT, json=request)

    assert orchestration_response.status_code == 200
    assert orchestration_response.json()["message"] == "Processing succeeded!"


@pytest.mark.integration
def test_process_endpoint_with_zip(setup):
    with open(
        Path(__file__).parent.parent.parent.parent.parent
        / "tests"
        / "assets"
        / "orchestration"
        / "test_zip.zip",
        "rb",
    ) as file:
        form_data = {
            "message_type": "ecr",
            "include_error_types": "errors",
        }
        files = {"upload_file": ("file.zip", file)}
        orchestration_response = httpx.post(
            PROCESS_ENDPOINT, data=form_data, files=files
        )
        assert orchestration_response.status_code == 200
        assert orchestration_response.json()["message"] == "Processing succeeded!"
