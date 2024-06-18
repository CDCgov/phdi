from pathlib import Path

import httpx
import pytest

VALIDATION_URL = "http://0.0.0.0:8080"
VALIDATE = VALIDATION_URL + "/validate"

test_error_types = ["errors", "warnings", "information"]


@pytest.mark.integration
def test_health_check(setup):
    health_check_response = httpx.get(VALIDATION_URL)
    assert health_check_response.status_code == 200


@pytest.mark.integration
def test_openapi():
    response = httpx.get(f"{VALIDATION_URL}/validation/openapi.json")
    assert response.status_code == 200
    assert "openapi" in response.json()


@pytest.mark.integration
def test_successful_ecr_conversion_rr_already_integrated(setup):
    message = open(
        Path(__file__).parent.parent.parent.parent.parent
        / "tests"
        / "assets"
        / "validation"
        / "ecr_sample_input_good_with_RR.xml"
    ).read()
    request = {
        "message_type": "ecr",
        "include_error_types": "errors",
        "message": message,
    }
    validation_response = httpx.post(VALIDATE, json=request)

    validation_response_body = validation_response.json()
    expected_response = {
        "fatal": [],
        "errors": [],
        "warnings": [],
        "information": [],
        "message_ids": {
            "eicr": {
                "root": "2.16.840.1.113883.9.9.9.9.9",
                "extension": "db734647-fc99-424c-a864-7e3cda82e704",
            },
            "rr": {
                "root": "4efa0e5c-c34c-429f-b5de-f1a13aef4a28",
                "extension": None,
            },
        },
    }

    assert validation_response.status_code == 200
    assert validation_response_body["message_valid"] is True
    assert validation_response_body["validation_results"] == expected_response


@pytest.mark.integration
def test_successful_ecr_conversion_with_rr_data(setup):
    message = open(
        Path(__file__).parent.parent.parent.parent.parent
        / "tests"
        / "assets"
        / "validation"
        / "ecr_sample_input_eICR_good.xml"
    ).read()
    rr_data = open(
        Path(__file__).parent.parent.parent.parent.parent
        / "tests"
        / "assets"
        / "validation"
        / "ecr_sample_input_RR_good.xml"
    ).read()

    request = {
        "message_type": "ecr",
        "include_error_types": "errors",
        "message": message,
        "rr_data": rr_data,
    }
    validation_response = httpx.post(VALIDATE, json=request)

    validation_response_body = validation_response.json()
    expected_response = {
        "fatal": [],
        "errors": [
            "Could not find field. Field name: 'Middle Name' Attributes: attribute #1: "
            "'qualifier' with the required value pattern: 'IN' Related elements: "
            "Field name: 'name' Attributes: attribute #1: 'use' with the required "
            "value pattern: 'L'",
            "Could not find field. Field name: 'Country'",
            "Could not find field. Field name: 'Provider ID' Attributes: attribute #1: "
            "'extension', attribute #2: 'root'",
        ],
        "warnings": [],
        "information": [],
        "message_ids": {
            "eicr": {
                "root": "1.2.840.114350.1.13.297.3.7.8.688883.567479",
                "extension": None,
            },
            "rr": {"root": "6c04db6f-5b50-4973-9f5c-a218ce9596e6", "extension": None},
        },
    }

    assert validation_response.status_code == 200
    assert validation_response_body["message_valid"] is True
    assert validation_response_body["validation_results"] == expected_response


@pytest.mark.integration
def test_ecr_validation_fails_with_invalid_xml(setup):
    request = {
        "message_type": "ecr",
        "include_error_types": "errors",
        "message": "sample eicr",
        "rr_data": "sample rr",
    }

    validation_response = httpx.post(VALIDATE, json=request)
    assert validation_response.status_code == 422
    assert validation_response.json()["detail"] == (
        "Reportability Response and eICR message both must be valid XML messages."
    )


@pytest.mark.integration
def test_validate_elr():
    request = {
        "message_type": "elr",
        "message": "my elr contents",
        "include_error_types": str(test_error_types),
    }
    validation_response = httpx.post(VALIDATE, json=request)
    validation_response_body = validation_response.json()
    assert validation_response.status_code == 200
    assert validation_response_body["message_valid"] is True
    assert validation_response_body["validation_results"]["details"] == (
        "No validation "
        "was actually performed. Validation for ELR is only stubbed currently."
    )


@pytest.mark.integration
def test_validate_vxu():
    request = {
        "message_type": "vxu",
        "message": "my vxu contents",
        "include_error_types": str(test_error_types),
    }
    validation_response = httpx.post(VALIDATE, json=request)
    validation_response_body = validation_response.json()
    assert validation_response.status_code == 200
    assert validation_response_body["message_valid"] is True
    assert validation_response_body["validation_results"]["details"] == (
        "No validation "
        "was actually performed. Validation for VXU is only stubbed currently."
    )


@pytest.mark.integration
def test_validate_fhir():
    request = {
        "message_type": "fhir",
        "message": "my fhir contents",
        "include_error_types": str(test_error_types),
    }
    validation_response = httpx.post(VALIDATE, json=request)
    validation_response_body = validation_response.json()
    assert validation_response.status_code == 200
    assert validation_response_body["message_valid"] is True
    assert validation_response_body["validation_results"]["details"] == (
        "No validation "
        "was actually performed. Validation for FHIR is only stubbed currently."
    )
