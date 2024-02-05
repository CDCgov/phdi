import json
import os
from pathlib import Path

import httpx
import pytest
from app.config import get_settings
from app.main import app
from starlette.testclient import TestClient

get_settings()

ORCHESTRATION_URL = "http://localhost:8080"
PROCESS_ENDPOINT = ORCHESTRATION_URL + "/process"
PROCESS_MESSAGE_ENDPOINT = ORCHESTRATION_URL + "/process-message"


@pytest.mark.integration
def test_health_check(setup):
    port_number_strings = [
        "ORCHESTRATION_PORT_NUMBER",
        "VALIDATION_PORT_NUMBER",
        "FHIR_CONVERTER_PORT_NUMBER",
        "INGESTION_PORT_NUMBER",
        "MESSAGE_PARSER_PORT_NUMBER",
    ]

    for port_number in port_number_strings:
        port = os.getenv(port_number)
        service_response = httpx.get(f"http://0.0.0.0:{port}")
        print(
            "Health check response for",
            port_number.replace("_PORT_NUMBER", ""),
            ":",
            service_response,
        )
        assert service_response.status_code == 200


@pytest.mark.integration
def test_process_message_endpoint(setup):
    message = open(
        Path(__file__).parent.parent.parent.parent.parent
        / "tests"
        / "assets"
        / "orchestration"
        / "CDA_eICR.xml"
    ).read()
    request = {
        "message_type": "ecr",
        "data_type": "ecr",
        "config_file_name": "sample-orchestration-config.json",
        "include_error_types": "errors",
        "message": message,
    }
    orchestration_response = httpx.post(PROCESS_MESSAGE_ENDPOINT, json=request)
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
            "config_file_name": "sample-orchestration-config.json",
            "include_error_types": "errors",
        }
        files = {"upload_file": ("file.zip", file)}
        orchestration_response = httpx.post(
            PROCESS_ENDPOINT, data=form_data, files=files
        )
        assert orchestration_response.status_code == 200
        assert orchestration_response.json()["message"] == "Processing succeeded!"


@pytest.mark.integration
def test_process_endpoint_with_zip_and_rr_data(setup):
    with open(
        Path(__file__).parent.parent.parent.parent.parent
        / "tests"
        / "assets"
        / "orchestration"
        / "eICR_RR_combo.zip",
        "rb",
    ) as file:
        form_data = {
            "message_type": "ecr",
            "config_file_name": "sample-orchestration-config.json",
            "include_error_types": "errors",
        }
        files = {"upload_file": ("file.zip", file)}
        orchestration_response = httpx.post(
            PROCESS_ENDPOINT, data=form_data, files=files
        )
        assert orchestration_response.status_code == 200
        assert orchestration_response.json()["message"] == "Processing succeeded!"
        assert (
            orchestration_response.json()["processed_values"]["parsed_values"]["rr_id"]
            is not None
        )


@pytest.mark.integration
def test_parse_message_fhir(setup):
    message = json.load(
        open(
            Path(__file__).parent.parent.parent
            / "assets"
            / "demo_phdc_conversion_bundle.json"
        )
    )
    request = {
        "message_type": "fhir",
        "data_type": "fhir",
        "config_file_name": "sample-fhir-test-config.json",
        "include_error_types": "errors",
        "message": message,
    }
    orchestration_response = httpx.post(PROCESS_MESSAGE_ENDPOINT, json=request)
    assert orchestration_response.status_code == 200
    assert orchestration_response.json()["message"] == "Processing succeeded!"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_websocket_process_message_endpoint(setup):
    expected_response_message = {
        "steps": [
            {"endpoint": "/validate", "service": "validation"},
            {"endpoint": "/convert-to-fhir", "service": "fhir_converter"},
            {
                "endpoint": "/fhir/harmonization/standardization/standardize_names",
                "service": "ingestion",
            },
            {
                "endpoint": "/fhir/harmonization/standardization/standardize_phones",
                "service": "ingestion",
            },
            {
                "endpoint": "/fhir/harmonization/standardization/standardize_dob",
                "service": "ingestion",
            },
            {"endpoint": "/parse_message", "service": "message_parser"},
            {"endpoint": "", "service": "save_to_db"},
        ],
        "validate": {
            "status": "success",
            "status_code": 200,
            "response": {
                "message_valid": True,
                "validation_results": {
                    "fatal": [],
                    "errors": [],
                    "warnings": [],
                    "information": [],
                    "message_ids": {
                        "eicr": {
                            "extension": None,
                            "root": "1.2.840.114350.1.13.297.3.7.8.688883.532013",
                        },
                        "rr": {},
                    },
                },
            },
        },
    }
    client = TestClient(app)

    # Pull in and read test zip file
    with open(
        Path(__file__).parent.parent.parent.parent.parent
        / "tests"
        / "assets"
        / "orchestration"
        / "test_zip.zip",
        "rb",
    ) as file:
        test_zip = file.read()

    # Create fake websocket connection
    with client.websocket_connect("/process-ws") as websocket:
        # Send zip into fake connection, triggering process-ws endpoint
        websocket.send_bytes(test_zip)

        # Pull response message from websocket connection like frontend would
        messages = websocket.receive_json()

    assert messages == expected_response_message
