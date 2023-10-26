from phdi.containers.base_service import BaseService
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket
from app.config import get_settings
from pathlib import Path

app = BaseService(
    service_name="PHDI Orchestration",
    description_path=Path(__file__).parent.parent / "description.md",
).start()

get_settings()


def test_websocket_process_message_endpoint():
    client = TestClient(app)

    with client.websocket_connect("/process-ws") as websocket:
        with open(
            Path(__file__).parent.parent.parent.parent
            / "tests"
            / "assets"
            / "orchestration"
            / "test_zip.zip",
            "rb",
        ) as file:
            websocket.send_json(file)

    assert data == {"msg": "Hello WebSocket"}
