import json
from copy import deepcopy
from pathlib import Path

from app.main import app
from fastapi.testclient import TestClient
from app import utils
from unittest import mock
from unittest.mock import patch
from datetime import date
import uuid

client = TestClient(app)

fhir_bundle_path = (
    Path(__file__).parent.parent / "assets" / "demo_phdc_conversion_bundle.json"
)

with open(fhir_bundle_path, "r") as file:
    fhir_bundle = json.load(file)

test_schema_path = (
    Path(__file__).parent.parent / "app" / "default_schemas" / "demo_phdc.json"
)

with open(test_schema_path, "r") as file:
    test_schema = json.load(file)

test_reference_schema_path = (
    Path(__file__).parent.parent
    / "app"
    / "default_schemas"
    / "test_reference_schema.json"
)

with open(test_reference_schema_path, "r") as file:
    test_reference_schema = json.load(file)

# TODO: Once we complete M2, the response type of the phdc endpoint will
# become PHDC rather than just JSON, so update the expected response
expected_successful_response = utils.read_file_from_assets("demo_phdc.xml")


@patch.object(uuid, "uuid4", lambda: "495669c7-96bf-4573-9dd8-59e745e05576")
@patch.object(utils, "get_datetime_now", lambda: date(2010, 12, 15))
def test_parse_message_success_internal_schema():
    test_request = {
        "parsing_schema_name": "demo_phdc.json",
        "message": fhir_bundle,
    }
    actual_response = client.post("/fhir_to_phdc", json=test_request)
    assert actual_response.status_code == 200
    assert actual_response.text == expected_successful_response


@patch.object(uuid, "uuid4", lambda: "495669c7-96bf-4573-9dd8-59e745e05576")
@patch.object(utils, "get_datetime_now", lambda: date(2010, 12, 15))
def test_parse_message_success_external_schema():
    request = {
        "parsing_schema": test_schema,
        "message": fhir_bundle,
    }

    actual_response = client.post("/fhir_to_phdc", json=request)
    assert actual_response.status_code == 200
    assert actual_response.text == expected_successful_response


def test_parse_message_internal_and_external_schema():
    request = {
        "parsing_schema": test_schema,
        "parsing_schema_name": "test_reference_schema.json",
        "message": {},
    }

    actual_response = client.post("/fhir_to_phdc", json=request)
    assert actual_response.status_code == 422
    assert (
        actual_response.json()["detail"][0]["msg"]
        == "Values for both 'parsing_schema' and 'parsing_schema_name' have been "
        "provided. Only one of these values is permited."
    )


def test_parse_message_neither_internal_nor_external_schema():
    request = {
        "message_format": "fhir",
        "message": {},
    }

    actual_response = client.post("/fhir_to_phdc", json=request)
    assert actual_response.status_code == 422
    assert (
        actual_response.json()["detail"][0]["msg"]
        == "Values for 'parsing_schema' and 'parsing_schema_name' have not been "
        "provided. One, but not both, of these values is required."
    )


def test_schema_without_reference_lookup():
    no_lookup_schema = deepcopy(test_reference_schema)
    del no_lookup_schema["labs"]["secondary_schema"]["ordering_provider"][
        "reference_lookup"
    ]
    request = {
        "message": {},
        "parsing_schema": no_lookup_schema,
    }

    actual_response = client.post("/fhir_to_phdc", json=request)
    assert actual_response.status_code == 422
    assert (
        actual_response.json()["detail"][0]["msg"]
        == "Secondary fields in the parsing schema that reference other "
        "resources must include a `reference_lookup` field that identifies "
        "where the reference ID can be found."
    )


def test_schema_without_identifier_path():
    no_bundle_schema = deepcopy(test_reference_schema)
    no_bundle_schema["labs"]["secondary_schema"]["ordering_provider"][
        "fhir_path"
    ] = "Observation.provider"
    request = {
        "message": {},
        "parsing_schema": no_bundle_schema,
    }

    actual_response = client.post("/fhir_to_phdc", json=request)
    assert actual_response.status_code == 422
    assert (
        actual_response.json()["detail"][0]["msg"]
        == "Secondary fields in the parsing schema that provide `reference_lookup` "
        "locations must have a `fhir_path` that begins with `Bundle` and identifies "
        "the type of resource being referenced."
    )
