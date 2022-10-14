import pathlib
import json
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

test_bundle = json.load(
    open(pathlib.Path(__file__).parent / "assets" / "single_patient_bundle.json")
)


# def test_add_patient_identifier_success():

#     test_request = {"data": test_bundle, "salt_str": "test_hash"}

#     expected_response = copy.deepcopy(test_bundle)
#     expected_response["entry"][0]["resource"]["identifier"] = [
#         {
#             "system": "urn:ietf:rfc:3986",
#             "use": "temp",
#           "value": "699d8585efcf84d1a03eb58e84cd1c157bf7b718d9257d7436e2ff0bd14b2834",
#         }
#     ]

#     actual_response = client.post(
#         "/fhir/linkage/link/add_patient_identifier", json=test_request
#     )
#     assert actual_response.json() == expected_response
