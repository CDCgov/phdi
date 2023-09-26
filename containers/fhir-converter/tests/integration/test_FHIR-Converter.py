import httpx
import pytest
from pathlib import Path

CONVERTER_URL = "http://0.0.0.0:8080"
CONVERT_TO_FHIR = CONVERTER_URL + "/convert-to-fhir"


@pytest.mark.integration
def test_health_check(setup):
    health_check_response = httpx.get(CONVERTER_URL)
    assert health_check_response.status_code == 200


@pytest.mark.integration
def test_vxu_conversion(setup):
    input_data = open(
        Path(__file__).parent.parent.parent / "assets" / "sample_request.hl7"
    ).read()
    request = {
        "input_data": input_data,
        "input_type": "vxu",
        "root_template": "VXU_V04",
    }
    vxu_conversion_response = httpx.post(CONVERT_TO_FHIR, json=request)

    assert vxu_conversion_response.status_code == 200
    assert (
        vxu_conversion_response.json()["response"]["FhirResource"]["resourceType"]
        == "Bundle"
    )


@pytest.mark.integration
def test_ecr_conversion(setup):
    input_data = open(
        Path(__file__).parent.parent.parent.parent.parent
        / "tests"
        / "assets"
        / "fhir-converter"
        / "ccda"
        / "ccda_sample.xml"
    ).read()
    request = {"input_data": input_data, "input_type": "ecr", "root_template": "EICR"}
    ecr_conversion_response = httpx.post(CONVERT_TO_FHIR, json=request)

    assert ecr_conversion_response.status_code == 200
    assert (
        ecr_conversion_response.json()["response"]["FhirResource"]["resourceType"]
        == "Bundle"
    )


@pytest.mark.integration
def test_ecr_conversion_with_rr(setup):
    rr_data = open(
        Path(__file__).parent.parent.parent.parent.parent
        / "tests"
        / "assets"
        / "fhir-converter"
        / "rr_extraction"
        / "CDA_RR.xml"
    ).read()
    input_data = open(
        Path(__file__).parent.parent.parent.parent.parent
        / "tests"
        / "assets"
        / "fhir-converter"
        / "rr_extraction"
        / "CDA_eICR.xml"
    ).read()
    request = {
        "input_data": input_data,
        "input_type": "ecr",
        "root_template": "EICR",
        "rr_data": rr_data,
    }
    ecr_conversion_response = httpx.post(CONVERT_TO_FHIR, json=request)

    assert ecr_conversion_response.status_code == 200
    assert (
        ecr_conversion_response.json()["response"]["FhirResource"]["resourceType"]
        == "Bundle"
    )


# This is returning a 500
# Shouldn't be doing that
@pytest.mark.integration
def test_invalid_rr_format(setup):
    request = {
        "input_data": "not valid xml",
        "input_type": "ecr",
        "root_template": "EICR",
        "rr_data": "also not valid xml",
    }
    ecr_conversion_response = httpx.post(CONVERT_TO_FHIR, json=request)

    assert ecr_conversion_response.status_code == 422
    assert (
        ecr_conversion_response.json()["detail"]
        == "Reportability Response and eICR message both "
        "must be valid XML messages."
    )
