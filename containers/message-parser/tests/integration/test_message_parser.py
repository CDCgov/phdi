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
            "patient_telecom": [
                {
                    "value": "555-690-3898",
                    "type": "home",
                    "useable_period_low": "2004-01-01",
                    "useable_period_high": "2010-02-02",
                },
                {
                    "value": "863-507-9999",
                    "type": "mobile",
                    "useable_period_low": "2008-03-18",
                    "useable_period_high": None,
                },
                {
                    "value": "kp73@gmail.com",
                    "type": None,
                    "useable_period_low": None,
                    "useable_period_high": None,
                },
            ],
            "author_time": "2022-08-08",
            "author_assigned_person": [
                {
                    "author_assigned_person_prefix": "Doctor",
                    "author_assigned_person_first": "Charles",
                    "author_assigned_person_middle": "Macintyre-Downing",
                    "author_assigned_person_family": "Britishmun",
                    "author_assigned_person_suffix": "III",
                }
            ],
            "custodian_represented_custodian_organization": [
                {
                    "name": "Sunny Vale",
                    "phone": "999-999-9999",
                    "street_address_line_1": "999 North Ridge Road",
                    "street_address_line_2": "Building 3",
                    "city": "Amherst",
                    "state": "Massachusetts",
                    "postal_code": None,
                    "county": "Duvall",
                    "country": None,
                }
            ],
            "clinical_information_observations": [
                {
                    "code": "15074-8",
                    "code_system": "http://loinc.org",
                    "code_display": "Glucose [Moles/volume] in Blood",
                    "quantitative_value": "6.3",
                    "quantitative_system": "http://unitsofmeasure.org",
                    "quantitative_code": "mmol/L",
                    "qualitative_value": None,
                    "qualitative_system": None,
                    "qualitative_code": None,
                },
                {
                    "code": "104177,600-7",
                    "code_system": "http://acmelabs.org,http://loinc.org",
                    "code_display": "Blood culture,Bacteria identified in Blood by Culture",  # noqa
                    "quantitative_value": None,
                    "quantitative_system": None,
                    "quantitative_code": None,
                    "qualitative_value": "Staphylococcus aureus",
                    "qualitative_system": "http://snomed.info/sct",
                    "qualitative_code": "3092008",
                },
            ],
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
