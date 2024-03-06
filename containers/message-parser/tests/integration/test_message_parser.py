import json
from pathlib import Path

import httpx
import pytest
from lxml import etree as ET
from rich.console import Console
from rich.table import Table

PARSER_URL = "http://0.0.0.0:8080"
PARSE_MESSAGE = PARSER_URL + "/parse_message"
FHIR_TO_PHDC = PARSER_URL + "/fhir_to_phdc"


def validate_xml(xml_input: ET.ElementTree) -> bool:
    """
    Validate the XML Element Tree against the XSD schema.

    :return: True if the XML is valid, False otherwise
    """
    console = Console()

    xsd_path = (
        Path(__file__).parent.parent.parent
        / "schema"
        / "extensions"
        / "SDTC"
        / "infrastructure"
        / "cda"
        / "CDA_SDTC.xsd"
    )

    with open(xsd_path, "rb") as xsd_file:
        xsd_tree = ET.XMLSchema(ET.parse(xsd_file))
        # print a confirmation message that the schema is loaded
        console.print("XSD schema loaded successfully", style="bold green")

    # validate the XML against the XSD
    is_valid = xsd_tree.validate(xml_input)

    # handling the results
    if is_valid:
        console.print(
            "the XML file is valid according to the XSD schema",
            style="bold green",
        )
        return True

    console.print("the XML file is not valid", style="bold red")
    # create the table for the error log
    table = Table(
        title="PHDC Validation", show_header=True, header_style="bold magenta"
    )

    # create the table columns to display the errors
    table.add_column("Line", style="dim", width=6, justify="right")
    table.add_column("Column", style="dim", width=6, justify="right")
    table.add_column("Message", overflow="fold")
    for error in xsd_tree.error_log:
        table.add_row(
            str(error.line),
            str(error.column),
            error.message,
        )
    console.print(table)
    return False


fhir_bundle_parse_message_path = (
    Path(__file__).parent.parent.parent
    / "tests"
    / "assets"
    / "demo_phdc_conversion_bundle.json"
)

fhir_bundle_fhir_to_phdc_path = (
    Path(__file__).parent.parent.parent
    / "tests"
    / "assets"
    / "sample_fhir_bundle_for_phdc_conversion.json"
)

test_schema_path = (
    Path(__file__).parent.parent.parent
    / "app"
    / "default_schemas"
    / "phdc_case_report_schema.json"
)

with open(fhir_bundle_parse_message_path, "r") as file:
    fhir_bundle_parse_message = json.load(file)

with open(fhir_bundle_fhir_to_phdc_path, "r") as file:
    fhir_bundle_fhir_to_phdc = json.load(file)

with open(test_schema_path, "r") as file:
    test_schema = json.load(file)


@pytest.mark.integration
def test_health_check(setup):
    health_check_response = httpx.get(PARSER_URL)
    assert health_check_response.status_code == 200


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
            "patient_race_display": "Asian",
            "patient_race_code": "2028-9",
            "patient_ethnic_group_display": "Not Hispanic or Latino",
            "patient_ethnic_group_code": "2186-5",
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
                    "obs_type": "vital-signs",
                    "code_code": "15074-8",
                    "code_code_system": "http://loinc.org",
                    "code_code_display": "Glucose [Moles/volume] in Blood",
                    "value_quantitative_value": "6.3",
                    "value_quant_code_system": "http://unitsofmeasure.org",
                    "value_quantitative_code": "mmol/L",
                    "value_qualitative_value": None,
                    "value_qualitative_code_system": None,
                    "value_qualitative_code": None,
                    "text": None,
                    "components": [],
                },
                {
                    "obs_type": "laboratory",
                    "code_code": "104177,600-7",
                    "code_code_system": "http://acmelabs.org,http://loinc.org",
                    "code_code_display": (
                        "Blood culture,Bacteria identified in Blood by Culture"
                    ),
                    "value_quantitative_value": None,
                    "value_quant_code_system": None,
                    "value_quantitative_code": None,
                    "value_qualitative_value": "Staphylococcus aureus",
                    "value_qualitative_code_system": "http://snomed.info/sct",
                    "value_qualitative_code": "3092008",
                    "text": None,
                    "components": [],
                },
                {
                    "obs_type": "social-history",
                    "code_code": "alcohol-type",
                    "code_code_system": "http://acme-rehab.org",
                    "code_code_display": "Type of alcohol consumed",
                    "value_quantitative_value": None,
                    "value_quant_code_system": None,
                    "value_quantitative_code": None,
                    "value_qualitative_value": None,
                    "value_qualitative_code_system": None,
                    "value_qualitative_code": None,
                    "text": None,
                    "components": [
                        {
                            "code_code": "alcohol-type",
                            "code_code_system": "http://acme-rehab.org",
                            "code_code_display": None,
                            "value_quantitative_value": None,
                            "value_quant_code_system": None,
                            "value_quantitative_code": None,
                            "value_qualitative_value": "Wine (substance)",
                            "value_qualitative_code_system": "http://snomed.info/sct",
                            "value_qualitative_code": "35748005",
                            "text": "Wine",
                        },
                        {
                            "code_code": "alcohol-type",
                            "code_code_system": "http://acme-rehab.org",
                            "code_code_display": None,
                            "value_quantitative_value": None,
                            "value_quant_code_system": None,
                            "value_quantitative_code": None,
                            "value_qualitative_value": "Beer (substance)",
                            "value_qualitative_code_system": "http://snomed.info/sct",
                            "value_qualitative_code": "53410008",
                            "text": "Beer",
                        },
                        {
                            "code_code": "alcohol-type",
                            "code_code_system": "http://acme-rehab.org",
                            "code_code_display": None,
                            "value_quantitative_value": None,
                            "value_quant_code_system": None,
                            "value_quantitative_code": None,
                            "value_qualitative_value": "Distilled spirits (substance)",
                            "value_qualitative_code_system": "http://snomed.info/sct",
                            "value_qualitative_code": "6524003",
                            "text": "Liquor",
                        },
                    ],
                },
                {
                    "obs_type": "EXPOS",
                    "code_code": "C3841750",
                    "code_code_system": "http://terminology.hl7.org/CodeSystem/umls",
                    "code_code_display": "Mass gathering",
                    "value_quantitative_value": None,
                    "value_quant_code_system": None,
                    "value_quantitative_code": None,
                    "value_qualitative_value": "Sports stadium (environment)",
                    "value_qualitative_code_system": "http://snomed.info/sct",
                    "value_qualitative_code": "264379009",
                    "text": "City Football Stadium",
                    "components": [
                        {
                            "code_code": "EXPAGNT",
                            "code_code_system": (
                                "http://terminology.hl7.org/CodeSystem/"
                                + "v3-ParticipationType"
                            ),
                            "code_code_display": "ExposureAgent",
                            "value_quantitative_value": None,
                            "value_quant_code_system": None,
                            "value_quantitative_code": None,
                            "value_qualitative_value": (
                                "Severe acute respiratory "
                                + "syndrome coronavirus 2 (organism)"
                            ),
                            "value_qualitative_code_system": "http://snomed.info/sct",
                            "value_qualitative_code": "840533007",
                            "text": None,
                        }
                    ],
                },
            ],
        },
    }

    request = {
        "message_format": "fhir",
        "parsing_schema": test_schema,
        "message": fhir_bundle_parse_message,
    }
    parsing_response = httpx.post(PARSE_MESSAGE, json=request)

    assert parsing_response.status_code == 200
    assert parsing_response.json() == expected_reference_response


@pytest.mark.integration
def test_fhir_to_phdc(setup):
    request = {"phdc_report_type": "case_report", "message": fhir_bundle_fhir_to_phdc}

    parsing_response = httpx.post(FHIR_TO_PHDC, json=request)

    assert parsing_response.status_code == 200

    parsed_output = ET.fromstring(parsing_response.text.encode())
    assert validate_xml(parsed_output)
