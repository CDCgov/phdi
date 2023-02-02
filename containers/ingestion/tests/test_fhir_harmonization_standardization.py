import pathlib
import json
import copy
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

test_bundle = json.load(
    open(pathlib.Path(__file__).parent / "assets" / "single_patient_bundle.json")
)


def test_standardize_names_success():
    expected_response = {
        "status_code": "200",
        "message": None,
        "bundle": copy.deepcopy(test_bundle),
    }
    expected_response["bundle"]["entry"][0]["resource"]["name"][0]["family"] = "SMITH"
    expected_response["bundle"]["entry"][0]["resource"]["name"][0]["given"][
        0
    ] = "DEEDEE"

    actual_response = client.post(
        "/fhir/harmonization/standardization/standardize_names",
        json={"data": test_bundle},
    )
    assert actual_response.json() == expected_response


def test_standardize_names_missing_data():
    actual_response = client.post(
        "/fhir/harmonization/standardization/standardize_names",
        json={},
    )
    assert actual_response.json() == {
        "detail": [
            {
                "loc": ["body", "data"],
                "msg": "field required",
                "type": "value_error.missing",
            }
        ]
    }


def test_standardize_names_not_fhir():
    invalid_bundle = copy.deepcopy(test_bundle)
    invalid_bundle["resourceType"] = ""

    actual_response = client.post(
        "/fhir/harmonization/standardization/standardize_names",
        json={"data": invalid_bundle},
    )

    assert actual_response.json() == {
        "detail": [
            {
                "loc": ["body", "data"],
                "msg": "Must provide a FHIR resource or bundle",
                "type": "assertion_error",
            }
        ]
    }


def test_standardize_names_bad_parameters():
    actual_response = client.post(
        "/fhir/harmonization/standardization/standardize_names",
        json={
            "data": test_bundle,
            "trim": "",
            "overwrite": "",
            "case": "",
            "remove_numbers": "",
        },
    )
    assert actual_response.json() == {
        "detail": [
            {
                "loc": ["body", "trim"],
                "msg": "value could not be parsed to a boolean",
                "type": "type_error.bool",
            },
            {
                "loc": ["body", "overwrite"],
                "msg": "value could not be parsed to a boolean",
                "type": "type_error.bool",
            },
            {
                "loc": ["body", "case"],
                "msg": "unexpected value; permitted: 'upper', 'lower', 'title'",
                "type": "value_error.const",
                "ctx": {"given": "", "permitted": ["upper", "lower", "title"]},
            },
            {
                "loc": ["body", "remove_numbers"],
                "msg": "value could not be parsed to a boolean",
                "type": "type_error.bool",
            },
        ]
    }


def test_standardize_phones_success():
    expected_response = {
        "status_code": "200",
        "message": None,
        "bundle": copy.deepcopy(test_bundle),
    }
    expected_response["bundle"]["entry"][0]["resource"]["telecom"][0][
        "value"
    ] = "+18015557777"

    actual_response = client.post(
        "/fhir/harmonization/standardization/standardize_phones",
        json={"data": test_bundle},
    )
    assert actual_response.json() == expected_response


def test_standardize_phones_missing_data():
    actual_response = client.post(
        "/fhir/harmonization/standardization/standardize_phones",
        json={},
    )
    assert actual_response.json() == {
        "detail": [
            {
                "loc": ["body", "data"],
                "msg": "field required",
                "type": "value_error.missing",
            }
        ]
    }


def test_standardize_phones_bad_overwrite_value():
    actual_response = client.post(
        "/fhir/harmonization/standardization/standardize_phones",
        json={
            "data": test_bundle,
            "overwrite": "",
        },
    )
    assert actual_response.json() == {
        "detail": [
            {
                "loc": ["body", "overwrite"],
                "msg": "value could not be parsed to a boolean",
                "type": "type_error.bool",
            }
        ]
    }
