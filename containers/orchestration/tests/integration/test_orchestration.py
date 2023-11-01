import httpx
import pytest
import os
from pathlib import Path
from phdi.containers.orchestration.app.config import get_settings
from phdi.containers.orchestration.app.main import app
from fastapi.websockets import WebSocketDisconnect
from fastapi.testclient import TestClient


get_settings()

ORCHESTRATION_URL = "http://localhost:8080"
PROCESS_ENDPOINT = ORCHESTRATION_URL + "/process"


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


@pytest.mark.asyncio
async def test_websocket_process_message_endpoint():
    client = TestClient(app)
    with open(
            Path(__file__).parent.parent.parent.parent.parent
            / "tests"
            / "assets"
            / "orchestration"
            / "test_zip.zip",
            "rb",
    ) as file:
        test_zip = file.read()

    with client.websocket_connect("/process-ws") as websocket:
        try:
            await websocket.send_bytes(test_zip)
            messages = await websocket.recv()
        except WebSocketDisconnect:
            pass

    assert messages == 'true'
