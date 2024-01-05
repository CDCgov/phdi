import copy
import json
import os
import pathlib

from app.config import get_settings
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

test_bundle = json.load(
    open(pathlib.Path(__file__).parent / "assets" / "single_patient_bundle.json")
)


def test_add_patient_identifier_in_bundle_success():
    test_request = {"bundle": test_bundle, "salt_str": "test_hash"}

    expected_response = {
        "status_code": "200",
        "message": None,
        "bundle": copy.deepcopy(test_bundle),
    }
    expected_response["bundle"]["entry"][0]["resource"]["identifier"] = [
        {
            "system": "urn:ietf:rfc:3986",
            "use": "temp",
            "value": "699d8585efcf84d1a03eb58e84cd1c157bf7b718d9257d7436e2ff0bd14b2834",
        }
    ]

    actual_response = client.post(
        "/fhir/linkage/link/add_patient_identifier_in_bundle", json=test_request
    )
    assert actual_response.json() == expected_response


def test_add_patient_identifier_in_bundle_missing_bundle():
    actual_response = client.post(
        "/fhir/linkage/link/add_patient_identifier_in_bundle", json={}
    )
    expected_response = {
        "detail": [
            {
                "loc": ["body", "bundle"],
                "msg": "field required",
                "type": "value_error.missing",
            }
        ]
    }
    assert actual_response.json() == expected_response


def test_add_patient_identifier_in_bundle_bad_parameter_types():
    test_request = {"bundle": test_bundle, "salt_str": [], "overwrite": 123}
    actual_response = client.post(
        "/fhir/linkage/link/add_patient_identifier_in_bundle", json=test_request
    )
    expected_response = {
        "detail": [
            {
                "loc": ["body", "salt_str"],
                "msg": "str type expected",
                "type": "type_error.str",
            },
            {
                "loc": ["body", "overwrite"],
                "msg": "value could not be parsed to a boolean",
                "type": "type_error.bool",
            },
        ]
    }
    assert actual_response.json() == expected_response


def test_add_patient_identifier_in_bundle_salt_from_env():
    os.environ.pop("CREDENTIAL_MANAGER", None)
    os.environ["SALT_STR"] = "test_hash"

    test_request = {"bundle": test_bundle}

    expected_response = {
        "status_code": "200",
        "message": None,
        "bundle": copy.deepcopy(test_bundle),
    }
    expected_response["bundle"]["entry"][0]["resource"]["identifier"] = [
        {
            "system": "urn:ietf:rfc:3986",
            "use": "temp",
            "value": "699d8585efcf84d1a03eb58e84cd1c157bf7b718d9257d7436e2ff0bd14b2834",
        }
    ]
    get_settings.cache_clear()
    actual_response = client.post(
        "/fhir/linkage/link/add_patient_identifier_in_bundle", json=test_request
    )
    assert actual_response.json() == expected_response


def test_add_patient_identifier_in_bundle_salt_from_env_missing():
    os.environ.pop("CREDENTIAL_MANAGER", None)
    os.environ.pop("SALT_STR", None)

    test_request = {"bundle": test_bundle}

    expected_message = (
        "The following values are required, but were not included in "
        "the request and could not be read from the environment. Please resubmit the "
        "request including these values or add them as environment variables to this "
        "service. missing values: salt_str."
    )
    expected_response = {
        "status_code": "400",
        "message": expected_message,
        "bundle": None,
    }
    get_settings.cache_clear()
    actual_response = client.post(
        "/fhir/linkage/link/add_patient_identifier_in_bundle", json=test_request
    )
    assert actual_response.json() == expected_response
