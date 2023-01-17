from azure.communication.identity import CommunicationIdentityClient
from azure.communication.phonenumbers import (
    PhoneNumbersClient,
    PhoneNumberCapabilityType,
    PhoneNumberAssignmentType,
    PhoneNumberType,
    PhoneNumberCapabilities,
)
from azure.communication.sms import SmsClient
from azure.identity import DefaultAzureCredential
from fastapi import FastAPI, Response, status
from pydantic import BaseModel, BaseSettings, Field
import pymsteams
from functools import lru_cache
from pathlib import Path
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from typing import Optional

# Instantiate FastAPI and set metadata.
description = Path("description.md").read_text(encoding="utf-8")
api = FastAPI(
    title="PHDI Alerts Service",
    version="0.0.1",
    contact={
        "name": "CDC Public Health Data Infrastructure",
        "url": "https://cdcgov.github.io/phdi-site/",
        "email": "dmibuildingblocks@cdc.gov",
    },
    license_info={
        "name": "Creative Commons Zero v1.0 Universal",
        "url": "https://creativecommons.org/publicdomain/zero/1.0/",
    },
    description=description,
)


class Settings(BaseSettings):
    """
    Environment variables needed for alerts.
    """

    communication_service_name: Optional[str]
    slack_bot_token: Optional[str]
    teams_webhook_url: Optional[str]


class SmsAlertInput(BaseModel):
    """
    Input parameters for SMS alerts.
    """

    phone_number: str = Field(description="The phone number to send the alert to.")
    message: str = Field(description="The message to send to the phone number.")


class SlackAlertInput(BaseModel):
    """
    Input parameters for Slack alerts.
    """

    channel_id: str = Field(description="The Slack channel ID to send the alert to.")
    message: str = Field(description="The message to send to the Slack channel.")


class TeamsAlertInput(BaseModel):
    """
    Input parameter for Teams alerts.
    """

    message: str = Field(description="The message to send to the Teams channel.")


@api.get("/")
async def health_check():
    """
    Check service status. If an HTTP 200 status code is returned along with
    '{"status": "OK"}' then the alerts service is available and running properly.
    """
    return {"status": "OK"}


@api.post("/sms-alert", status_code=200)
async def sms_alert(input: SmsAlertInput, response: Response):
    """
    Send an SMS alert to a phone number.
    :param input: A JSON formated request body with schema specified by the
        SmsAlertInput model.
    """

    env = check_for_environment_variables()
    communication_service_name = env.get("communication_service_name")
    if communication_service_name is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return "The communication_service_name environment variable is not set."

    endpoint = f"https://{communication_service_name}.communication.azure.com"
    credential = DefaultAzureCredential()
    from_number = get_phone_number(endpoint, credential)["phone_number"]
    create_identity_and_get_token(endpoint, credential)
    return send_sms(
        endpoint,
        credential,
        from_number,
        input.phone_number,
        input.message,
    )


@api.post("/slack-alert", status_code=200)
async def slack_alert(input: SlackAlertInput, response: Response):
    """
    Send a Slack alert to a channel.
    :param input: A JSON formated request body with schema specified by the
        SlackAlertInput model.
    """

    env = check_for_environment_variables()
    slack_bot_token = env.get("slack_bot_token")
    if slack_bot_token is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return "The slack_bot_token environment variable is not set."

    client = WebClient(token=slack_bot_token)

    try:
        res = client.chat_postMessage(
            channel=input.channel_id,
            text=input.message,
        )
        return res.data
    except SlackApiError as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return e.response


@api.post("/teams-alert", status_code=200)
async def teams_alert(input: TeamsAlertInput, response: Response):
    """
    Send a Teams alert to a channel.
    :param input: A JSON formated request body with schema specified by the
        TeamsAlertInput model.
    """

    env = check_for_environment_variables()
    teams_webhook_url = env.get("teams_webhook_url")
    if teams_webhook_url is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return "The teams_webhook_url environment variable is not set."

    myTeamsMessage = pymsteams.connectorcard(teams_webhook_url)
    myTeamsMessage.text(input.message)
    return myTeamsMessage.send()


@lru_cache()
def get_settings() -> dict:
    """
    Load the values specified in the Settings class from the environment and return a
    dictionary containing them. The dictionary is cached to reduce overhead accessing
    these values.

    :return: A dictionary with keys specified by the Settings. The value of each key is
    read from the corresponding environment variable.
    """
    return Settings().dict()


def check_for_environment_variables():
    """
    Read the environment variables needed for alerts and return a dictionary containing
    them.
    """

    return {
        "communication_service_name": get_settings().get("communication_service_name"),
        "slack_bot_token": get_settings().get("slack_bot_token"),
        "teams_webhook_url": get_settings().get("teams_webhook_url"),
    }


def get_phone_number(endpoint, credential):
    """
    Purchase a phone number to use for sending SMS messages, or find an existing phone
    number that has already been purchased.
    """

    phone_numbers_client = PhoneNumbersClient(endpoint, credential)
    capabilities = PhoneNumberCapabilities(
        calling=PhoneNumberCapabilityType.OUTBOUND,
        sms=PhoneNumberCapabilityType.OUTBOUND,
    )

    # Check if any phone numbers have already been purchased
    purchased_phone_numbers = check_for_purchased_phone_numbers(phone_numbers_client)
    if purchased_phone_numbers["status"] == "Purchased":
        return purchased_phone_numbers

    search_poller = phone_numbers_client.begin_search_available_phone_numbers(
        "US",
        PhoneNumberType.TOLL_FREE,
        PhoneNumberAssignmentType.APPLICATION,
        capabilities,
        quantity=1,
        polling=True,
    )
    search_result = search_poller.result()

    purchase_poller = phone_numbers_client.begin_purchase_phone_numbers(
        search_result.search_id, polling=True
    )
    purchase_poller.result()

    return check_for_purchased_phone_numbers(phone_numbers_client)


def check_for_purchased_phone_numbers(phone_numbers_client):
    """
    Check if any phone numbers have already been purchased.
    """

    purchased_phone_numbers = phone_numbers_client.list_purchased_phone_numbers()
    for purchased_phone_number in purchased_phone_numbers:
        return {
            "status": "Purchased",
            "phone_number": purchased_phone_number.phone_number,
        }
    return {"status": "No phone numbers purchased"}


def create_identity_and_get_token(resource_endpoint, credential):
    """
    Create a new user identity and get a token for that identity.
    """

    client = CommunicationIdentityClient(resource_endpoint, credential)
    client.create_user_and_token(scopes=["voip"])


def send_sms(
    resource_endpoint, credential, from_phone_number, to_phone_number, message_content
):
    """
    Send an SMS message.
    """

    sms_client = SmsClient(resource_endpoint, credential)

    response = sms_client.send(
        from_=from_phone_number,
        to=[to_phone_number],
        message=message_content,
        enable_delivery_report=True,
    )
    return response
