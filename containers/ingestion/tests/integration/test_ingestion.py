import httpx
import pytest

PARSER_URL = "http://0.0.0.0:8080"
PARSE_MESSAGE = PARSER_URL + "/parse_message"
FHIR_TO_PHDC = PARSER_URL + "/fhir_to_phdc"


@pytest.fixture
def fhir_bundle(read_json_from_test_assets):
    return read_json_from_test_assets("single_patient_bundle.json")


@pytest.mark.integration
def test_health_check(setup):
    health_check_response = httpx.get(PARSER_URL)
    assert health_check_response.status_code == 200


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
    parsing_response = httpx.post(PARSE_MESSAGE, json=request)

    assert parsing_response.status_code == 200
    assert parsing_response.json() == expected_reference_response
