import time
import httpx
import pytest
from pathlib import Path
from icecream import ic

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

    validation_response_body = orchestration_response

    ic(validation_response_body)

    assert validation_response_body is "cheese"

# @pytest.mark.integration
# def test_process_endpoint_with_zipfile(setup):

