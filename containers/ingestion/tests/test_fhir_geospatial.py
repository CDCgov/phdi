import json
import os
import pathlib
from unittest import mock

from app.config import get_settings
from app.main import app
from fastapi import Response
from fastapi import status
from fastapi.testclient import TestClient

client = TestClient(app)


test_bundle = json.load(
    open(pathlib.Path(__file__).parent / "assets" / "single_patient_bundle.json")
)


@mock.patch("app.routers.fhir_geospatial.SmartyFhirGeocodeClient")
def test_geocode_bundle_returns_errors_from_smarty(patched_smarty_client):
    test_request = {
        "bundle": test_bundle,
        "geocode_method": "smarty",
        "smarty_auth_id": "test_id",
        "smarty_auth_token": "test_token",
    }

    expected_response = {
        "status_code": "400",
        "message": "Smarty raised the following exception: I am a test error message",
        "bundle": None,
    }

    patched_smarty_client.return_value.geocode_bundle.side_effect = Exception(
        "I am a test error message"
    )
    actual_response = client.post(
        "/fhir/geospatial/geocode/geocode_bundle", json=test_request
    )

    assert actual_response.json() == expected_response


@mock.patch("app.routers.fhir_geospatial.CensusFhirGeocodeClient")
def test_geocode_bundle_success_census(patched_client):
    test_request = {"bundle": test_bundle, "geocode_method": "census"}

    client.post("/fhir/geospatial/geocode/geocode_bundle", json=test_request)

    patched_client.return_value.geocode_bundle.assert_called_with(
        bundle=test_bundle, overwrite=True
    )


@mock.patch("app.routers.fhir_geospatial.SmartyFhirGeocodeClient")
def test_geocode_bundle_success_smarty(patched_client):
    test_request = {
        "bundle": test_bundle,
        "geocode_method": "smarty",
        "smarty_auth_id": "test_id",
        "smarty_auth_token": "test_token",
    }

    client.post("/fhir/geospatial/geocode/geocode_bundle", json=test_request)

    patched_client.return_value.geocode_bundle.assert_called_with(
        bundle=test_bundle, overwrite=True
    )


def test_geocode_bundle_no_method():
    test_request = {"bundle": test_bundle, "geocode_method": ""}
    expected_response = 422
    actual_response = client.post(
        "/fhir/geospatial/geocode/geocode_bundle", json=test_request
    )
    assert actual_response.status_code == expected_response


def test_geocode_bundle_wrong_method():
    test_request = {"bundle": test_bundle, "geocode_method": "wrong"}
    expected_response = 422
    actual_response = client.post(
        "/fhir/geospatial/geocode/geocode_bundle", json=test_request
    )
    assert expected_response == actual_response.status_code


def test_geocode_bundle_smarty_no_auth_id():
    test_request = {
        "bundle": test_bundle,
        "geocode_method": "smarty",
        "smarty_auth_id": None,
        "smarty_auth_token": "test_token",
    }
    expected_message = (
        "The following values are required, but "
        "were not included in the request and could not be read from the environment."
        " Please resubmit the request including these values or add them as "
        "environment variables to this service. missing values: smarty_auth_id."
    )
    expected_response = {
        "status_code": "400",
        "message": expected_message,
        "bundle": None,
    }
    get_settings.cache_clear()
    os.environ.pop("SMARTY_AUTH_ID", None)
    actual_response = client.post(
        "/fhir/geospatial/geocode/geocode_bundle", json=test_request
    )
    assert actual_response.json() == expected_response


def test_geocode_bundle_smarty_no_auth_token():
    test_request = {
        "bundle": test_bundle,
        "geocode_method": "smarty",
        "smarty_auth_id": "test_id",
        "smarty_auth_token": None,
    }
    expected_message = (
        "The following values are required, but were not included "
        "in the request and could not be read from the environment. Please "
        "resubmit the request including these values or add them as "
        "environment variables to this service. missing values: smarty_auth_token."
    )
    expected_response = {
        "status_code": "400",
        "message": expected_message,
        "bundle": None,
    }
    get_settings.cache_clear()
    os.environ.pop("AUTH_TOKEN", None)

    actual_response = client.post(
        "/fhir/geospatial/geocode/geocode_bundle", json=test_request
    )
    assert actual_response.json() == expected_response


@mock.patch("app.routers.fhir_geospatial.SmartyFhirGeocodeClient")
@mock.patch("app.routers.fhir_geospatial.geocode_bundle_endpoint")
def test_geocode_bundle_bad_smarty_creds_env(patched_geocode, patched_smarty_client):
    test_request = {
        "bundle": test_bundle,
        "geocode_method": "smarty",
        "smarty_auth_id": "",
        "smarty_auth_token": "",
    }
    os.environ["SMARTY_AUTH_ID"] = "test_id"
    os.environ["SMARTY_AUTH_TOKEN"] = "test_token"
    get_settings.cache_clear()
    error = ""
    expected_response = Response
    expected_response.status_code = status.HTTP_400_BAD_REQUEST
    expected_response.json = {"error": error}
    patched_smarty_client.return_value.geocode_bundle = expected_response
    patched_geocode.geocode_client = patched_smarty_client
    actual_response = client.post(
        "/fhir/geospatial/geocode/geocode_bundle", json=test_request
    )

    assert actual_response.status_code == expected_response.status_code
    os.environ.pop("SMARTY_AUTH_ID", None)
    os.environ.pop("SMARTY_AUTH_TOKEN", None)
