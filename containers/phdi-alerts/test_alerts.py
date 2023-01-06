# flake8: noqa
import os
from unittest import mock
from fastapi.testclient import TestClient
from types import SimpleNamespace

from main import api

client = TestClient(api)


def test_health_check():
    actual_response = client.get("/")
    assert actual_response.status_code == 200
    assert actual_response.json() == {"status": "OK"}


@mock.patch("main.DefaultAzureCredential")
@mock.patch("main.send_sms")
@mock.patch("main.create_identity_and_get_token")
@mock.patch("main.get_phone_number")
@mock.patch("main.check_for_environment_variables")
def test_sms_alert(
    patched_check_for_environment_variables,
    patched_get_phone_number,
    patched_create_identity_and_get_token,
    patched_send_sms,
    patched_default_azure_credential,
):
    patched_get_phone_number.return_value = {"phone_number": "+18338675309"}
    patched_check_for_environment_variables.return_value = {
        "communication_service_name": "test_communication_service_name",
    }
    valid_request = {
        "phone_number": "+11234567890",
        "message": "test message",
    }
    valid_response = [
        {
            "additional_properties": {},
            "to": "+11234567890",
            "message_id": "Outgoing_20221230182750489be2c7-03ea-4692-956d-6e794055e969_noam",
            "http_status_code": 202,
            "successful": True,
            "error_message": None,
        }
    ]
    patched_send_sms.return_value = valid_response
    actual_response = client.post("/sms-alert", json=valid_request)
    assert actual_response.status_code == 200
    assert actual_response.json() == valid_response


@mock.patch("main.check_for_environment_variables")
def test_sms_alert_missing_communication_service_name(
    patched_check_for_environment_variables,
):
    patched_check_for_environment_variables.return_value = {
        "communication_service_name": None,
    }
    valid_request = {
        "phone_number": "+11234567890",
        "message": "test message",
    }
    actual_response = client.post("/sms-alert", json=valid_request)
    assert actual_response.status_code == 400
    assert (
        actual_response.json()
        == "The communication_service_name environment variable is not set."
    )


@mock.patch("main.WebClient")
@mock.patch("main.check_for_environment_variables")
def test_slack_alert(patched_check_for_environment_variables, patched_web_client):
    valid_response = {"data": {"ok": True}}
    namespace = SimpleNamespace(**valid_response)
    patched_web_client.return_value.chat_postMessage.return_value = namespace
    patched_check_for_environment_variables.return_value = {
        "slack_bot_token": "test_slack_bot_token",
    }
    valid_request = {
        "channel_id": "test_channel_id",
        "message": "test message",
    }
    actual_response = client.post("/slack-alert", json=valid_request)
    assert actual_response.status_code == 200
    assert actual_response.json() == namespace.data


@mock.patch("main.check_for_environment_variables")
def test_slack_alert_missing_slack_bot_token(patched_check_for_environment_variables):
    patched_check_for_environment_variables.return_value = {
        "slack_bot_token": None,
    }
    valid_request = {
        "channel_id": "test_channel_id",
        "message": "test message",
    }
    actual_response = client.post("/slack-alert", json=valid_request)
    assert actual_response.status_code == 400
    assert (
        actual_response.json() == "The slack_bot_token environment variable is not set."
    )


@mock.patch("main.pymsteams")
@mock.patch("main.check_for_environment_variables")
def test_teams_alert(patched_check_for_environment_variables, patched_pymsteams):
    patched_check_for_environment_variables.return_value = {
        "teams_webhook_url": "test_teams_webhook",
    }
    patched_pymsteams.connectorcard.return_value.send.return_value = "Message sent"
    valid_request = {
        "message": "test message",
    }
    actual_response = client.post("/teams-alert", json=valid_request)
    assert actual_response.status_code == 200
    assert actual_response.json() == "Message sent"


@mock.patch("main.check_for_environment_variables")
def test_teams_alert_missing_teams_webhook_url(patched_check_for_environment_variables):
    patched_check_for_environment_variables.return_value = {
        "teams_webhook_url": None,
    }
    valid_request = {
        "message": "test message",
    }
    actual_response = client.post("/teams-alert", json=valid_request)
    assert actual_response.status_code == 400
    assert (
        actual_response.json()
        == "The teams_webhook_url environment variable is not set."
    )
