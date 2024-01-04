from app.services import (
    validation_payload,
    ingestion_payload,
    fhir_converter_payload,
    message_parser_payload,
)
from requests.models import Response


def test_validation_payload():
    result = validation_payload(input={"message": "foo"})
    expected_result = {
        "message_type": "ecr",
        "include_error_types": "errors",
        "message": "foo",
        "rr_data": None,
    }
    assert result == expected_result


def test_validation_payload_with_rr():
    result = validation_payload(input={"message": "foo", "rr_data": "bar"})
    expected_result = {
        "message_type": "ecr",
        "include_error_types": "errors",
        "message": "foo",
        "rr_data": "bar",
    }
    assert result == expected_result


def test_fhir_converter_payload():
    result = fhir_converter_payload(input={"message": "foo"})
    expected_result = {
        "input_data": "foo",
        "input_type": "ecr",
        "root_template": "EICR",
        "rr_data": None,
    }

    assert result == expected_result


def test_fhir_converter_payload_with_rr():
    result = fhir_converter_payload(input={"message": "foo", "rr_data": "bar"})
    expected_result = {
        "input_data": "foo",
        "input_type": "ecr",
        "root_template": "EICR",
        "rr_data": "bar",
    }

    assert result == expected_result


def test_ingestion_payload():
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
        "license_type": '"us-rooftop-geocoding-enterprise-cloud"',
        "smarty_auth_id": '"placeholder"',
        "smarty_auth_token": '"placeholder"',
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
        }
    }
    result = message_parser_payload(response=response, config=config)
    expected_result = {
        "message": "bar",
        "message_format": "msg_format",
        "parsing_schema_name": "schema_name",
    }

    assert result == expected_result
