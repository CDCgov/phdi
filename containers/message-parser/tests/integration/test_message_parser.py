import json
from pathlib import Path

import httpx
import pytest

PARSER_URL = "http://0.0.0.0:8080"
PARSE_MESSAGE = PARSER_URL + "/parse_message"
FHIR_TO_PHDC = PARSER_URL + "/fhir_to_phdc"


@pytest.mark.integration
def test_health_check(setup):
    health_check_response = httpx.get(PARSER_URL)
    assert health_check_response.status_code == 200


reference_bundle_path = (
    Path(__file__).parent.parent.parent.parent.parent
    / "tests"
    / "assets"
    / "general"
    / "patient_bundle_w_labs.json"
)

with open(reference_bundle_path, "r") as file:
    reference_bundle = json.load(file)

test_reference_schema_path = (
    Path(__file__).parent.parent.parent
    / "app"
    / "default_schemas"
    / "test_reference_schema.json"
)

with open(test_reference_schema_path, "r") as file:
    test_reference_schema = json.load(file)


@pytest.mark.integration
def test_parse_message(setup):
    expected_reference_response = {
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

    request = {
        "message_format": "fhir",
        "parsing_schema": test_reference_schema,
        "message": reference_bundle,
    }

    parsing_response = httpx.post(PARSE_MESSAGE, json=request)

    assert parsing_response.status_code == 200
    assert parsing_response.json() == expected_reference_response


@pytest.mark.integration
def test_fhir_to_phdc(setup):
    request = {
        "parsing_schema": test_reference_schema,
        "message": reference_bundle,
    }

    parsing_response = httpx.post(FHIR_TO_PHDC, json=request)

    # TODO: Once the PHDC builder work is completed, this test can be
    # developed further to check the structure and content of the
    # generated PHDC message.
    assert parsing_response.status_code == 200
