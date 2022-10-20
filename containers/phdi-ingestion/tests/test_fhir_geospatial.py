import pathlib
import os
import json
import copy
from re import A
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

test_bundle = json.load(
    open(pathlib.Path(__file__).parent / "assets" / "single_patient_bundle.json")
)


def test_geocode_bundle_bad_smarty_creds():

    test_request = {"bundle": test_bundle, "geocode_method": "smarty", "auth_id": "test_id", "auth_token": "test_token"}

    with pytest.raises(Exception):
        actual_response = client.post(
        "/fhir/geospatial/geocode/geocode_bundle", json=test_request
    )

def test_geocode_bundle_success_census():
    test_request = {"bundle": test_bundle, "geocode_method": "census"}
    expected_response = copy.deepcopy(test_bundle)
    expected_response["entry"][0]["resource"]["address"][0]["street"] = "123 Main St."
    actual_response = client.post(
        "/fhir/geospatial/geocode/geocode_bundle", json=test_request
    )
    assert actual_response.json() == expected_response

def test_geocode_bundle_no_method():
    test_request = {"bundle": test_bundle, "geocode_method": ""}
    expected_response = copy.deepcopy(test_bundle)

    expected_response = 422
    actual_response = client.post(
        "/fhir/geospatial/geocode/geocode_bundle", json=test_request
    )
    assert actual_response.status_code == expected_response

def test_geocode_bundle_wrong_method():
    test_request = {"bundle": test_bundle, "geocode_method": "wrong"}
    expected_response = copy.deepcopy(test_bundle)

    expected_response = 422
    actual_response = client.post(
        "/fhir/geospatial/geocode/geocode_bundle", json=test_request
    )
    assert actual_response.status_code == expected_response

def test_geocode_bundle_smarty_no_auth_id():
    test_request = {"bundle": test_bundle, "geocode_method": "smarty", "auth_id": None, "auth_token": "test_token"}
    expected_response = copy.deepcopy(test_bundle)

    try:
        actual_response = client.post(
            "/fhir/geospatial/geocode/geocode_bundle", json=test_request
        )
    except Exception as error:
        print("my_error")
        print(error)
        assert 1 == 2

    #print(actual_response.json())
    #assert actual_response.json() == expected_response


# def test_add_patient_identifier_in_bundle_missing_bundle():
# expected_response = copy.deepcopy(test_bundle)
#     expected_response["entry"][0]["resource"]["identifier"] = [
#         {
#             "system": "urn:ietf:rfc:3986",
#             "use": "temp",
#             "value": "699d8585efcf84d1a03eb58e84cd1c157bf7b718d9257d7436e2ff0bd14b2834",
#         }
#     ]


#     actual_response = client.post(
#         "/fhir/linkage/link/add_patient_identifier_in_bundle", json={}
#     )
#     expected_response = {
#         "detail": [
#             {
#                 "loc": ["body", "bundle"],
#                 "msg": "field required",
#                 "type": "value_error.missing",
#             }
#         ]
#     }
#     assert actual_response.json() == expected_response


# def test_add_patient_identifier_in_bundle_bad_parameter_types():

#     test_request = {"bundle": test_bundle, "salt_str": [], "overwrite": 123}
#     actual_response = client.post(
#         "/fhir/linkage/link/add_patient_identifier_in_bundle", json=test_request
#     )
#     expected_response = {
#         "detail": [
#             {
#                 "loc": ["body", "salt_str"],
#                 "msg": "str type expected",
#                 "type": "type_error.str",
#             },
#             {
#                 "loc": ["body", "overwrite"],
#                 "msg": "value could not be parsed to a boolean",
#                 "type": "type_error.bool",
#             },
#         ]
#     }
#     assert actual_response.json() == expected_response


# def test_add_patient_identifier_in_bundle_salt_from_env():
#     os.environ.pop("CREDENTIAL_MANAGER", None)
#     os.environ["SALT_STR"] = "test_hash"

#     test_request = {"bundle": test_bundle}

#     expected_response = copy.deepcopy(test_bundle)
#     expected_response["entry"][0]["resource"]["identifier"] = [
#         {
#             "system": "urn:ietf:rfc:3986",
#             "use": "temp",
#             "value": "699d8585efcf84d1a03eb58e84cd1c157bf7b718d9257d7436e2ff0bd14b2834",
#         }
#     ]
#     get_settings.cache_clear()
#     actual_response = client.post(
#         "/fhir/linkage/link/add_patient_identifier_in_bundle", json=test_request
#     )
#     assert actual_response.json() == expected_response


# def test_add_patient_identifier_in_bundle_salt_from_env_missing():
#     os.environ.pop("CREDENTIAL_MANAGER", None)
#     os.environ.pop("SALT_STR", None)

#     test_request = {"bundle": test_bundle}

#     expected_response = (
#         "The following values are required, but were not included in "
#         "the request and could not be read from the environment. Please resubmit the "
#         "request including these values or add them as environment variables to this "
#         "service. missing values: salt_str."
#     )
#     get_settings.cache_clear()
#     actual_response = client.post(
#         "/fhir/linkage/link/add_patient_identifier_in_bundle", json=test_request
#     )
#     assert actual_response.json() == expected_response



# @mock.patch("app.routers.fhir_geospatial_smarty.get_smartystreets_client")
# @mock.patch("app.routers.fhir_geospatial_smarty.geocode_patients")
# def test_geocode_bundle_success(
#     patched_geocode_patients, patched_get_smartystreets_client
# ):

#     request_body = {
#         "data": test_bundle,
#         "auth_id": "some-auth-id",
#         "auth_token": "some-auth-toke",
#     }

#     geocoder = mock.Mock()
#     patched_get_smartystreets_client.return_value = geocoder

#     client.post("/fhir/geospatial/smarty/gecode_bundle", json=request_body)

#     patched_geocode_patients.assert_called_with(bundle=test_bundle, client=geocoder)
