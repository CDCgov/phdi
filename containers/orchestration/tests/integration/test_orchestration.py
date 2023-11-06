import httpx
import pytest
import os
from pathlib import Path
from app.config import get_settings
from app.main import app
from starlette.websockets import WebSocket
from fastapi.testclient import TestClient
from starlette.types import Receive, Scope, Send
from starlette.testclient import TestClient


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
    print('other test')
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


# @pytest.mark.asyncio
# @pytest.mark.integration
# async def test_websocket_process_message_endpoint():
#     print('Hello')
#     client = TestClient(app)
#     with open(
#             Path(__file__).parent.parent.parent.parent.parent
#             / "tests"
#             / "assets"
#             / "orchestration"
#             / "test_zip.zip",
#             "rb",
#     ) as file:
#         test_zip = file.read()
#
#     with client.websocket_connect("/process-ws") as websocket:
#
#         await websocket.accept()
#         await websocket.send_bytes(test_zip)
#         await websocket.close()
#         messages = await websocket.recv()
#
#     assert "red" == messages


@pytest.mark.asyncio
@pytest.mark.integration
def test_websocket_send_and_receive_bytes(test_client_factory):
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.accept()
        data = await websocket.receive_bytes()
        await websocket.send_bytes(b"Message was: " + data)
        await websocket.close()

    client = test_client_factory(app)
    with client.websocket_connect("/") as websocket:
        websocket.send_bytes(b"Hello, world!")
        data = websocket.receive_bytes()
        assert data == b"Message was: Hello, world!"
