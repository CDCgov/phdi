import pathlib
import json

# from unittest import mock
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

test_bundle = json.load(
    open(pathlib.Path(__file__).parent / "assets" / "single_patient_bundle.json")
)


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
