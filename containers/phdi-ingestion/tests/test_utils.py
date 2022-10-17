from unittest import mock
import pytest
from app.utils import (
    check_for_environment_variables,
    check_for_fhir,
    check_for_fhir_bundle,
)


@mock.patch("app.utils.os.environ")
def test_check_for_environment_variables_success(patched_environ):
    environment_variables = ["SOME-ENV-VAR"]
    patched_environ.get.return_value = "some-value"
    actual_response = check_for_environment_variables(environment_variables)
    expected_response = {
        "status_code": 200,
        "message": "All environment variables were found.",
    }
    assert actual_response == expected_response


@mock.patch("app.utils.os.environ")
def test_check_for_environment_variables_failure(patched_environ):
    environment_variables = ["SOME-ENV-VAR"]
    patched_environ.get.return_value = None
    actual_response = check_for_environment_variables(environment_variables)
    expected_response = {
        "status_code": 500,
        "message": (
            "Environment variable 'SOME-ENV-VAR' not set. "
            "The environment variable must be set."
        ),
    }
    assert actual_response == expected_response


def test_check_for_fhir():
    good_fhir = {"resourceType": "Patient"}
    assert check_for_fhir(good_fhir) == good_fhir

    bad_fhir = {}
    with pytest.raises(AssertionError):
        check_for_fhir(bad_fhir)


def test_check_for_fhir_bundle():
    good_fhir = {"resourceType": "Bundle"}
    assert check_for_fhir_bundle(good_fhir) == good_fhir

    bad_fhir = {"resourceType": "Patient"}
    with pytest.raises(AssertionError):
        check_for_fhir_bundle(bad_fhir)
