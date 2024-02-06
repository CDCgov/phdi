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
    Path(__file__).parent.parent.parent
    / "app"
    / "default_schemas"
    / "phdc_case_report_schema.json"
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
            "patient_race_code": "2028-9",
            "patient_race_display": "Asian",
            "patient_ethnic_group_code": "2186-5",
            "patient_ethnic_group_display": "Not Hispanic or Latino",
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
                    "prefix": "Doctor",
                    "first": "Charles",
                    "middle": "Macintyre-Downing",
                    "family": "Britishmun",
                    "suffix": "III",
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
                    "postal_code": "33721",
                    "county": "Duvall",
                    "country": None,
                }
            ],
            "observations": [
                {
                    "obs_type": "laboratory",
                    "code_code": "15074-8",
                    "code_code_system": "http://loinc.org",
                    "code_code_display": "Glucose [Moles/volume] in Blood",
                    "value_quantitative_value": "6.3",
                    "value_quantitative_code_system": "http://unitsofmeasure.org",
                    "value_quantitative_code": "mmol/L",
                    "value_qualitative_value": None,
                    "value_qualitative_code_system": None,
                    "value_qualitative_code": None,
                },
                {
                    "obs_type": "laboratory",
                    "code_code": "104177,600-7",
                    "code_code_system": "http://acmelabs.org,http://loinc.org",
                    "code_code_display": "Blood culture,Bacteria identified in Blood by Culture",  # noqa
                    "value_quantitative_value": None,
                    "value_quantitative_code_system": None,
                    "value_quantitative_code": None,
                    "value_qualitative_value": "Staphylococcus aureus",
                    "value_qualitative_code_system": "http://snomed.info/sct",
                    "value_qualitative_code": "3092008",
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
        "phdc_report_type": "case_report",
        "message": test_bundle,
    }

    parsing_response = httpx.post(FHIR_TO_PHDC, json=request)

    # TODO: Once the PHDC builder work is completed, this test can be
    # developed further to check the structure and content of the
    # generated PHDC message.
    assert parsing_response.status_code == 200
