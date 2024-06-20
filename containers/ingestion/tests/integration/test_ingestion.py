import httpx
import pytest

INGESTION_URL = "http://0.0.0.0:8080"
INGESTION_EXTENSION = "/fhir/harmonization/standardization"
NAMES_URL = INGESTION_URL + INGESTION_EXTENSION + "/standardize_names"
PHONE_URL = INGESTION_URL + INGESTION_EXTENSION + "/standardize_phones"
DOB_URL = INGESTION_URL + INGESTION_EXTENSION + "/standardize_dob"


@pytest.fixture
def fhir_bundle(read_json_from_test_assets):
    return read_json_from_test_assets("single_patient_bundle.json")


@pytest.mark.integration
def test_health_check(setup):
    health_check_response = httpx.get(INGESTION_URL)
    assert health_check_response.status_code == 200


@pytest.mark.integration
def test_openapi():
    actual_response = httpx.get(INGESTION_URL + "/ingestion/openapi.json")
    assert actual_response.status_code == 200


@pytest.mark.integration
def test_standardize_names(setup, fhir_bundle):
    expected_reference_response = {
        "status_code": "200",
        "message": None,
        "bundle": {
            "resourceType": "Bundle",
            "id": "bundle-transaction",
            "meta": {"lastUpdated": "2018-03-11T11:22:16Z"},
            "type": "transaction",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Patient",
                        "name": [
                            {"family": "SMITH", "given": ["DEEDEE"], "use": "official"}
                        ],
                        "gender": "female",
                        "telecom": [{"system": "phone", "value": "8015557777"}],
                        "address": [
                            {
                                "line": ["123 Main St."],
                                "city": "Anycity",
                                "state": "CA",
                                "postalCode": "12345",
                                "country": "USA",
                            }
                        ],
                        "birthDate": "1955-11-05",
                    },
                    "request": {"method": "POST", "url": "Patient"},
                }
            ],
        },
    }

    request = {"data": fhir_bundle}
    parsing_response = httpx.post(NAMES_URL, json=request)

    assert parsing_response.status_code == 200
    assert parsing_response.json() == expected_reference_response


@pytest.mark.integration
def test_standardize_phone(setup, fhir_bundle):
    expected_reference_response = {
        "status_code": "200",
        "message": None,
        "bundle": {
            "resourceType": "Bundle",
            "id": "bundle-transaction",
            "meta": {"lastUpdated": "2018-03-11T11:22:16Z"},
            "type": "transaction",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Patient",
                        "name": [
                            {"family": "Smith", "given": ["DeeDee"], "use": "official"}
                        ],
                        "gender": "female",
                        "telecom": [{"system": "phone", "value": "+18015557777"}],
                        "address": [
                            {
                                "line": ["123 Main St."],
                                "city": "Anycity",
                                "state": "CA",
                                "postalCode": "12345",
                                "country": "USA",
                            }
                        ],
                        "birthDate": "1955-11-05",
                    },
                    "request": {"method": "POST", "url": "Patient"},
                }
            ],
        },
    }

    request = {"data": fhir_bundle}
    parsing_response = httpx.post(PHONE_URL, json=request)

    assert parsing_response.status_code == 200
    assert parsing_response.json() == expected_reference_response


@pytest.mark.integration
def test_standardize_dob(setup, fhir_bundle):
    expected_reference_response = {
        "status_code": "200",
        "message": None,
        "bundle": {
            "resourceType": "Bundle",
            "id": "bundle-transaction",
            "meta": {"lastUpdated": "2018-03-11T11:22:16Z"},
            "type": "transaction",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Patient",
                        "name": [
                            {"family": "Smith", "given": ["DeeDee"], "use": "official"}
                        ],
                        "gender": "female",
                        "telecom": [{"system": "phone", "value": "8015557777"}],
                        "address": [
                            {
                                "line": ["123 Main St."],
                                "city": "Anycity",
                                "state": "CA",
                                "postalCode": "12345",
                                "country": "USA",
                            }
                        ],
                        "birthDate": "1955-11-05",
                    },
                    "request": {"method": "POST", "url": "Patient"},
                }
            ],
        },
    }

    request = {"data": fhir_bundle}
    parsing_response = httpx.post(DOB_URL, json=request)

    assert parsing_response.status_code == 200
    assert parsing_response.json() == expected_reference_response
