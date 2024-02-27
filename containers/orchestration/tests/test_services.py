import os
from pathlib import Path

import pytest
from app.services import fhir_converter_payload
from app.services import ingestion_payload
from app.services import message_parser_payload
from app.services import save_to_db_payload
from app.services import validation_payload
from fastapi import HTTPException
from requests.models import Response

from phdi.fhir.conversion.convert import standardize_hl7_datetimes


def test_validation_payload():
    result = validation_payload(input={"message": "foo", "message_type": "ecr"})
    expected_result = {
        "message_type": "ecr",
        "include_error_types": "errors",
        "message": "foo",
        "rr_data": None,
    }
    assert result == expected_result


def test_validation_payload_with_rr():
    result = validation_payload(
        input={"message": "foo", "message_type": "ecr", "rr_data": "bar"}
    )
    expected_result = {
        "message_type": "ecr",
        "include_error_types": "errors",
        "message": "foo",
        "rr_data": "bar",
    }
    assert result == expected_result


def test_fhir_converter_payload():
    message = open(
        Path(__file__).parent.parent.parent.parent
        / "tests"
        / "assets"
        / "fhir-converter"
        / "hl7v2"
        / "hl7_with_msh_3_set.hl7"
    ).read()
    result = fhir_converter_payload(input={"message": message})
    assert result["input_type"] == "hl7v2"
    assert result["root_template"] == "ADT_A01"
    assert result["input_data"] == standardize_hl7_datetimes(message)


def test_fhir_converter_payload_with_rr():
    message = open(
        Path(__file__).parent.parent.parent.parent
        / "tests"
        / "assets"
        / "fhir-converter"
        / "ecr"
        / "example_eicr.xml"
    ).read()
    rr = open(
        Path(__file__).parent.parent.parent.parent
        / "tests"
        / "assets"
        / "fhir-converter"
        / "ecr"
        / "example_rr.xml"
    ).read()
    result = fhir_converter_payload(input={"message": message, "rr_data": rr})
    expected_result = {
        "input_data": message,
        "input_type": "ecr",
        "root_template": "EICR",
        "rr_data": rr,
    }

    assert result == expected_result


def test_ingestion_payload():
    os.environ["SMARTY_AUTH_ID"] = "placeholder"
    os.environ["SMARTY_AUTH_TOKEN"] = "placeholder"
    os.environ["LICENSE_TYPE"] = "us-rooftop-geocoding-enterprise-cloud"
    response = Response()
    response.status_code = 200
    response._content = b'{"bundle": "bar", "response":{"FhirResource":"fiz"}}'
    result = ingestion_payload(response=response, step="bar", config="biz")
    assert result == {"data": "bar"}

    step = {
        "service": "ingestion",
        "endpoint": "/standardize_names",
    }
    result = ingestion_payload(
        response=response,
        step=step,
        config="biz",
    )
    assert result == {"data": "fiz"}

    step = {
        "service": "ingestion",
        "endpoint": "/geocode",
    }
    config = {
        "configurations": {
            "ingestion": {
                "standardization_and_geocoding": {"geocode_method": "code_method"}
            }
        }
    }

    result = ingestion_payload(
        response=response,
        step=step,
        config=config,
    )
    expected_result = {
        "bundle": "bar",
        "geocode_method": "code_method",
        "license_type": "us-rooftop-geocoding-enterprise-cloud",
        "smarty_auth_id": "placeholder",
        "smarty_auth_token": "placeholder",
    }
    assert result == expected_result


def test_message_parser_payload():
    response = Response()
    response.status_code = 200
    response._content = b'{"bundle": "bar", "response":{"FhirResource":"fiz"}}'
    config = {
        "configurations": {
            "message_parser": {
                "message_format": "msg_format",
                "parsing_schema_name": "schema_name",
            }
        },
        "steps": [{"service": "message_parser", "endpoint": "/parse-message"}],
    }
    result = message_parser_payload(response=response, config=config)
    expected_result = {
        "message": "bar",
        "message_format": "msg_format",
        "parsing_schema_name": "schema_name",
    }

    assert result == expected_result


def test_save_to_db_payload():
    response = Response()
    response.status_code = 200
    response._content = b'{"bundle": {"entry": [{"resource": {"id": "foo"}}]}}'
    result = save_to_db_payload(bundle=response)
    expected_result = {
        "data": {"entry": [{"resource": {"id": "foo"}}]},
        "ecr_id": "foo",
    }

    assert result == expected_result


def test_save_to_db_failure_missing_eicr_id():
    response = Response()
    response.status_code = 200
    response._content = b'{"bundle": "bar", "parsed_values":{}}'

    with pytest.raises(HTTPException) as exc_info:
        save_to_db_payload(bundle=response)

    assert exc_info.value.status_code == 422
