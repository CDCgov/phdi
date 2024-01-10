import json
from copy import deepcopy
from pathlib import Path

from app.main import app
from fastapi.testclient import TestClient


client = TestClient(app)

fhir_bundle_path = (
    Path(__file__).parent.parent.parent.parent
    / "tests"
    / "assets"
    / "general"
    / "patient_bundle_w_labs.json"
)

with open(fhir_bundle_path, "r") as file:
    fhir_bundle = json.load(file)

test_schema_path = (
    Path(__file__).parent.parent
    / "app"
    / "default_schemas"
    / "test_reference_schema.json"
)

with open(test_schema_path, "r") as file:
    test_schema = json.load(file)

expected_successful_response = {
    "message": "Parsing succeeded!",
    "parsed_values": {
        "first_name": "John ",
        "last_name": "doe",
        "labs": [
            {
                "test_type": "Blood culture",
                "test_result_code_display": "Staphylococcus aureus",
                "ordering_provider": "Western Pennsylvania Medical General",
                "requesting_organization_contact_person": "Dr. Totally Real Doctor, M.D.",  # noqa
            }
        ],
    },
}


def test_parse_message_success_internal_schema():
    test_request = {
        "parsing_schema_name": "test_reference_schema.json",
        "message": fhir_bundle,
    }

    actual_response = client.post("/fhir_to_phdc", json=test_request)
    assert actual_response.status_code == 200
    assert actual_response.json() == expected_successful_response


def test_parse_message_success_external_schema():
    request = {
        "parsing_schema": test_schema,
        "message": fhir_bundle,
    }

    actual_response = client.post("/fhir_to_phdc", json=request)
    assert actual_response.status_code == 200
    assert actual_response.json() == expected_successful_response


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
    no_lookup_schema = deepcopy(test_schema)
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
    no_bundle_schema = deepcopy(test_schema)
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
