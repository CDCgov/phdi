from phdi.containers.base_service import BaseService
from fastapi.testclient import TestClient
from app.config import get_settings
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
import pytest
from fastapi.websockets import WebSocketDisconnect
from icecream import ic
from app.main import app
from unittest import mock
import asyncio

get_settings()


# @pytest.mark.asyncio
# async def test_websocket_process_message_endpoint():
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
#     mock_sum.return_value = 'wat'
#     with client.websocket_connect("/process-ws") as websocket:
#         try:
#             await websocket.send_bytes(test_zip)
#         except WebSocketDisconnect:
#             pass
#
#     mock_sum.assert_called_with("true")


# @pytest.mark.asyncio
# async def test_process_message_endpoint_ws():
#     client = TestClient(app)
#     url = "ws://testserver/process-ws"
#
#     with patch("path.to.your.call_apis") as mock_call_apis:
#         async with client.websocket_connect(url) as websocket:
#             # Sending some sample data
#             sample_zipped_file = create_sample_zipped_file()  # Replace with a function that returns a sample zipped file as bytes
#             await websocket.send_bytes(sample_zipped_file)
#
#             # Additional logic to ensure that WebSocket messages are received and processed
#             # ...
#
#             # Assert that call_apis was called
#             mock_call_apis.assert_called()