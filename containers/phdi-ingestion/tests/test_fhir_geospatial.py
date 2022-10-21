import pathlib
import os
import json
import copy
from unittest import mock
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import get_settings


client = TestClient(app)


test_bundle = json.load(
    open(pathlib.Path(__file__).parent / "assets" / "single_patient_bundle.json")
)


def test_geocode_bundle_bad_smarty_creds():

    test_request = {
        "bundle": test_bundle,
        "geocode_method": "smarty",
        "auth_id": "test_id",
        "auth_token": "test_token",
    }
    with pytest.raises(Exception):
        client.post("/fhir/geospatial/geocode/geocode_bundle", json=test_request)


@mock.patch("app.routers.fhir_geospatial.geocode_client")
def test_geocode_bundle_success_census(patched_client):
    test_request = {"bundle": test_bundle, "geocode_method": "census"}
    #expected_response = copy.deepcopy(test_bundle)
    #expected_response["entry"][0]["resource"]["address"][0]["street"] = "123 Main St."
    patched_census_client = mock.Mock()
    patched_client.return_value = patched_census_client
    client.post(
        "/fhir/geospatial/geocode/geocode_bundle", json=test_request
    )
    patched_census_client.geocode_bundle.assert_called_with(
        bundle=test_bundle
    )
    #print(actual_response)
    #print(actual_response.json())


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
        "auth_id": None,
        "auth_token": "test_token",
    }
    expected_response = (
        "The following values are required, but "
        "were not included in the request and could not be read from the environment."
        " Please resubmit the request including these values or add them as "
        "environment variables to this service. missing values: auth_id."
    )
    get_settings.cache_clear()
    os.environ.pop("AUTH_ID", None)
    actual_response = client.post(
        "/fhir/geospatial/geocode/geocode_bundle", json=test_request
    )
    assert actual_response.json() == expected_response


def test_geocode_bundle_smarty_no_auth_token():
    test_request = {
        "bundle": test_bundle,
        "geocode_method": "smarty",
        "auth_id": "test_id",
        "auth_token": None,
    }
    expected_response = (
        "The following values are required, but were not included "
        "in the request and could not be read from the environment. Please "
        "resubmit the request including these values or add them as "
        "environment variables to this service. missing values: auth_token."
    )
    get_settings.cache_clear()
    os.environ.pop("AUTH_TOKEN", None)

    actual_response = client.post(
        "/fhir/geospatial/geocode/geocode_bundle", json=test_request
    )
    assert actual_response.json() == expected_response


def test_geocode_bundle_bad_smarty_creds_env():
    test_request = {
        "bundle": test_bundle,
        "geocode_method": "smarty",
        "auth_id": "",
        "auth_token": "",
    }
    os.environ["AUTH_ID"] = "test_id"
    os.environ["AUTH_TOKEN"] = "test_token"
    get_settings.cache_clear()
    with pytest.raises(Exception):
        client.post("/fhir/geospatial/geocode/geocode_bundle", json=test_request)
    os.environ.pop("AUTH_ID", None)
    os.environ.pop("AUTH_TOKEN", None)
