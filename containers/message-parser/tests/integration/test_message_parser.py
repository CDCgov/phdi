import httpx
import pytest
from lxml import etree as ET

PARSER_URL = "http://0.0.0.0:8080"
PARSE_MESSAGE = PARSER_URL + "/parse_message"
FHIR_TO_PHDC = PARSER_URL + "/fhir_to_phdc"


@pytest.fixture
def fhir_bundle(read_json_from_test_assets):
    return read_json_from_test_assets("sample_fhir_bundle_for_phdc_conversion.json")


@pytest.fixture
def test_schema(read_schema_from_default_schemas):
    return read_schema_from_default_schemas("phdc_case_report_schema.json")


@pytest.mark.integration
def test_health_check(setup):
    health_check_response = httpx.get(PARSER_URL)
    assert health_check_response.status_code == 200


@pytest.mark.integration
def test_openapi():
    actual_response = httpx.get(PARSER_URL + "/message-parser/openapi.json")
    assert actual_response.status_code == 200


@pytest.mark.integration
def test_parse_message(setup, test_schema, fhir_bundle):
    expected_reference_response = {
        "message": "Parsing succeeded!",
        "parsed_values": {
            "patient_address": [
                {
                    "street_address_line_1": "6 Watery Lighthouse Trailer Park Way",
                    "street_address_line_2": "Unit #2",
                    "city": "Watery",
                    "state": "WA",
                    "postal_code": "98440",
                    "county": None,
                    "country": "United States",
                    "type": "home",
                    "useable_period_low": None,
                    "useable_period_high": None,
                }
            ],
            "patient_name": [
                {
                    "prefix": "Ms.",
                    "first": "Saga",
                    "middle": None,
                    "family": "Anderson",
                    "suffix": None,
                    "type": "official",
                    "valid_time_low": None,
                    "valid_time_high": None,
                }
            ],
            "patient_administrative_gender_code": "female",
            "patient_race_display": "Black or African American",
            "patient_race_code": "2054-5",
            "patient_ethnic_group_display": "Not Hispanic or Latino",
            "patient_ethnic_group_code": "2186-5",
            "patient_birth_time": "1987-11-11",
            "patient_telecom": [
                {
                    "value": "206-555-0123",
                    "type": "home",
                    "useable_period_low": None,
                    "useable_period_high": None,
                }
            ],
            "author_time": "2024-02-07",
            "author_assigned_person": [
                {
                    "prefix": "Dr.",
                    "first": "Emma",
                    "middle": None,
                    "family": "Nelson",
                    "suffix": None,
                }
            ],
            "custodian_represented_custodian_organization": [
                {
                    "name": "Nelson Family Practice",
                    "phone": "206-555-0199",
                    "street_address_line_1": "123 Harbor St",
                    "street_address_line_2": None,
                    "city": "Bright Falls",
                    "state": "WA",
                    "postal_code": "98440",
                    "county": None,
                    "country": "United States",
                }
            ],
            "observations": [
                {
                    "obs_type": None,
                    "code_code": "INV163",
                    "code_code_system": "2.16.840.1.114222.4.5.232",
                    "code_code_display": "Case Status",
                    "value_quantitative_value": None,
                    "value_quant_code_system": None,
                    "value_quantitative_code": None,
                    "value_qualitative_value": "Confirmed",
                    "value_qualitative_code_system": "2.16.840.1.113883.6.96",
                    "value_qualitative_code": "410605003",
                    "text": None,
                    "components": [],
                },
                {
                    "obs_type": None,
                    "code_code": "INV169",
                    "code_code_system": "2.16.840.1.114222.4.5.232",
                    "code_code_display": "Condition",
                    "value_quantitative_value": None,
                    "value_quant_code_system": None,
                    "value_quantitative_code": None,
                    "value_qualitative_value": "Hepatitis A, acute",
                    "value_qualitative_code_system": "2.16.840.1.114222.4.5.277",
                    "value_qualitative_code": "10110",
                    "text": None,
                    "components": [],
                },
                {
                    "obs_type": "social-history",
                    "code_code": "DEM127",
                    "code_code_system": "2.16.840.1.114222.4.5.232",
                    "code_code_display": "Is this person deceased?",
                    "value_quantitative_value": None,
                    "value_quant_code_system": None,
                    "value_quantitative_code": None,
                    "value_qualitative_value": "No",
                    "value_qualitative_code_system": "2.16.840.1.113883.12.136",
                    "value_qualitative_code": "N",
                    "text": None,
                    "components": [],
                },
                {
                    "obs_type": "social-history",
                    "code_code": "NBS104",
                    "code_code_system": "2.16.840.1.114222.4.5.1",
                    "code_code_display": "Information As of Date",
                    "value_quantitative_value": None,
                    "value_quant_code_system": None,
                    "value_quantitative_code": None,
                    "value_qualitative_value": "2024-01-24",
                    "value_qualitative_code_system": None,
                    "value_qualitative_code": None,
                    "text": None,
                    "components": [],
                },
                {
                    "obs_type": "social-history",
                    "code_code": "INV2001",
                    "code_code_system": "2.16.840.1.114222.4.5.232",
                    "code_code_display": "Reported Age",
                    "value_quantitative_value": None,
                    "value_quant_code_system": None,
                    "value_quantitative_code": None,
                    "value_qualitative_value": "36",
                    "value_qualitative_code_system": None,
                    "value_qualitative_code": None,
                    "text": None,
                    "components": [],
                },
                {
                    "obs_type": "social-history",
                    "code_code": "INV2002",
                    "code_code_system": "2.16.840.1.114222.4.5.232",
                    "code_code_display": "Reported Age Units",
                    "value_quantitative_value": None,
                    "value_quant_code_system": None,
                    "value_quantitative_code": None,
                    "value_qualitative_value": "year [time]",
                    "value_qualitative_code_system": "2.16.840.1.113883.6.8",
                    "value_qualitative_code": "a",
                    "text": None,
                    "components": [],
                },
                {
                    "obs_type": None,
                    "code_code": "INV163",
                    "code_code_system": "2.16.840.1.114222.4.5.232",
                    "code_code_display": "Case Status",
                    "value_quantitative_value": None,
                    "value_quant_code_system": None,
                    "value_quantitative_code": None,
                    "value_qualitative_value": "Confirmed",
                    "value_qualitative_code_system": "2.16.840.1.113883.6.96",
                    "value_qualitative_code": "410605003",
                    "text": None,
                    "components": [],
                },
                {
                    "obs_type": None,
                    "code_code": "INV169",
                    "code_code_system": "2.16.840.1.114222.4.5.232",
                    "code_code_display": "Condition",
                    "value_quantitative_value": None,
                    "value_quant_code_system": None,
                    "value_quantitative_code": None,
                    "value_qualitative_value": "Hepatitis A, acute",
                    "value_qualitative_code_system": "2.16.840.1.114222.4.5.277",
                    "value_qualitative_code": "10110",
                    "text": None,
                    "components": [],
                },
                {
                    "obs_type": None,
                    "code_code": "NBS055",
                    "code_code_system": "2.16.840.1.114222.4.5.1",
                    "code_code_display": "Contact Investigation Priority",
                    "value_quantitative_value": None,
                    "value_quant_code_system": None,
                    "value_quantitative_code": None,
                    "value_qualitative_value": "Low",
                    "value_qualitative_code_system": "L",
                    "value_qualitative_code": "LOW",
                    "text": None,
                    "components": [],
                },
                {
                    "obs_type": None,
                    "code_code": "NBS058",
                    "code_code_system": "2.16.840.1.114222.4.5.1",
                    "code_code_display": "Contact Investigation Status",
                    "value_quantitative_value": None,
                    "value_quant_code_system": None,
                    "value_quantitative_code": None,
                    "value_qualitative_value": "In progress",
                    "value_qualitative_code_system": "2.16.840.1.113883.6.96",
                    "value_qualitative_code": "385651009",
                    "text": None,
                    "components": [],
                },
                {
                    "obs_type": None,
                    "code_code": "INV148",
                    "code_code_system": "2.16.840.1.114222.4.5.232",
                    "code_code_display": "Is this person associated "
                    + "with a day care facility?",
                    "value_quantitative_value": None,
                    "value_quant_code_system": None,
                    "value_quantitative_code": None,
                    "value_qualitative_value": "Yes",
                    "value_qualitative_code_system": "2.16.840.1.113883.12.136",
                    "value_qualitative_code": "Y",
                    "text": None,
                    "components": [],
                },
                {
                    "obs_type": "EXPOS",
                    "code_code": "69730-0",
                    "code_code_system": "http://loinc.org",
                    "code_code_display": "Questionnaire Document",
                    "value_quantitative_value": None,
                    "value_quant_code_system": None,
                    "value_quantitative_code": None,
                    "value_qualitative_value": None,
                    "value_qualitative_code_system": None,
                    "value_qualitative_code": None,
                    "text": None,
                    "components": [
                        {
                            "code_code": "INV502",
                            "code_code_system": "2.16.840.1.113883.6.1",
                            "code_code_display": "Country of Exposure",
                            "value_quantitative_value": None,
                            "value_quant_code_system": None,
                            "value_quantitative_code": None,
                            "value_qualitative_value": "UNITED STATES",
                            "value_qualitative_code_system": "1.0.3166.1",
                            "value_qualitative_code": "USA",
                            "text": None,
                        },
                        {
                            "code_code": "INV503",
                            "code_code_system": "2.16.840.1.113883.6.1",
                            "code_code_display": "State or Province of Exposure",
                            "value_quantitative_value": None,
                            "value_quant_code_system": None,
                            "value_quantitative_code": None,
                            "value_qualitative_value": "Washington",
                            "value_qualitative_code_system": "2.16.840.1.113883.6.92",
                            "value_qualitative_code": "53",
                            "text": None,
                        },
                        {
                            "code_code": "INV504",
                            "code_code_system": "2.16.840.1.113883.6.1",
                            "code_code_display": "City of Exposure",
                            "value_quantitative_value": None,
                            "value_quant_code_system": None,
                            "value_quantitative_code": None,
                            "value_qualitative_value": "Bright Falls",
                            "value_qualitative_code_system": None,
                            "value_qualitative_code": None,
                            "text": None,
                        },
                        {
                            "code_code": "INV505",
                            "code_code_system": "2.16.840.1.113883.6.1",
                            "code_code_display": "County of Exposure",
                            "value_quantitative_value": None,
                            "value_quant_code_system": None,
                            "value_quantitative_code": None,
                            "value_qualitative_value": "Pierce County",
                            "value_qualitative_code_system": "2.16.840.1.113883.6.93",
                            "value_qualitative_code": "053",
                            "text": None,
                        },
                    ],
                },
            ],
        },
    }

    request = {
        "message_format": "fhir",
        "parsing_schema": test_schema,
        "message": fhir_bundle,
    }
    parsing_response = httpx.post(PARSE_MESSAGE, json=request)

    assert parsing_response.status_code == 200
    assert parsing_response.json() == expected_reference_response


@pytest.mark.integration
def test_fhir_to_phdc(setup, fhir_bundle, validate_xml):
    request = {"phdc_report_type": "case_report", "message": fhir_bundle}

    parsing_response = httpx.post(FHIR_TO_PHDC, json=request)

    assert parsing_response.status_code == 200

    parsed_output = ET.fromstring(parsing_response.text.encode())
    assert validate_xml(parsed_output)
