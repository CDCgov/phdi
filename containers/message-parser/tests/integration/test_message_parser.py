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


fhir_bundle_path = (
    Path(__file__).parent.parent.parent / "assets" / "demo_phdc_conversion_bundle.json"
)

with open(fhir_bundle_path, "r") as file:
    test_bundle = json.load(file)

test_schema_path = (
    Path(__file__).parent.parent.parent / "app" / "default_schemas" / "demo_phdc.json"
)

with open(test_schema_path, "r") as file:
    test_schema = json.load(file)


@pytest.mark.integration
def test_parse_message(setup):
    expected_reference_response = {
        "message": "Parsing succeeded!",
        "parsed_values": {
            "patient_address": [
                {
                    "street_address_line_1": "165 Eichmann Crossing",
                    "street_address_line_2": "Suite 25",
                    "city": "Waltham",
                    "state": "Massachusetts",
                    "postal_code": "46239",
                    "county": "Franklin",
                    "country": "US",
                    "type": "official",
                    "useable_period_low": None,
                    "useable_period_high": None,
                }
            ],
            "patient_name": [
                {
                    "prefix": "Mrs.",
                    "first": "Kimberley",
                    "middle": "Annette",
                    "family": "Price",
                    "suffix": None,
                    "type": "official",
                    "valid_time_low": None,
                    "valid_time_high": None,
                },
                {
                    "prefix": "Ms.",
                    "first": "Kim",
                    "middle": None,
                    "family": "Levinson",
                    "suffix": None,
                    "type": "maiden",
                    "valid_time_low": "1996-04-17",
                    "valid_time_high": "2022-12-03",
                },
            ],
            "patient_administrative_gender_code": "female",
            "patient_race_code": None,
            "patient_ethnic_group_code": None,
            "patient_birth_time": "1996-04-17",
        },
    }

    request = {
        "message_format": "fhir",
        "parsing_schema": test_schema,
        "message": test_bundle,
    }

    parsing_response = httpx.post(PARSE_MESSAGE, json=request)

    assert parsing_response.status_code == 200
    assert parsing_response.json() == expected_reference_response


@pytest.mark.integration
def test_fhir_to_phdc(setup):
    request = {
        "parsing_schema": test_schema,
        "message": test_bundle,
    }

    parsing_response = httpx.post(FHIR_TO_PHDC, json=request)

    # TODO: Once the PHDC builder work is completed, this test can be
    # developed further to check the structure and content of the
    # generated PHDC message.
    assert parsing_response.status_code == 200
