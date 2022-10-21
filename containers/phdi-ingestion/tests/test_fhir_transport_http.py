import os
import pathlib
import json
import copy
from fastapi.testclient import TestClient
from unittest import mock

from app.main import app
from app.config import get_settings

client = TestClient(app)

test_bundle = json.load(
    open(pathlib.Path(__file__).parent / "assets" / "single_patient_bundle.json")
)


fhir_server_response_body = json.load(
    open(pathlib.Path(__file__).parent / "assets" / "upload_response.json")
)


@mock.patch("app.routers.fhir_transport_http.upload_bundle_to_fhir_server")
@mock.patch("app.routers.fhir_transport_http.credential_managers")
@mock.patch("app.routers.fhir_transport_http.AzureCredentialManager")
def test_upload_bundle_to_fhir_server_request_params_success(
    patched_azure_cred_manager, patched_cred_managers, patched_bundle_upload
):
    test_request = {
        "bundle": test_bundle,
        "credential_manager": "azure",
        "fhir_url": "some-FHIR-server-URL",
    }

    patched_cred_managers.__getitem__.side_effect = {
        "azure": patched_azure_cred_manager
    }.__getitem__

    fhir_server_response = mock.Mock()
    fhir_server_response.status_code = 200
    fhir_server_response.json.return_value = fhir_server_response_body
    patched_bundle_upload.return_value = fhir_server_response

    actual_response = client.post(
        "/fhir/transport/http/upload_bundle_to_fhir_server", json=test_request
    )

    patched_bundle_upload.assert_called_with(
        bundle=test_bundle,
        credential_manager=patched_azure_cred_manager,
        fhir_url=test_request["fhir_url"],
    )
    assert actual_response.status_code == 200
    assert actual_response.json() == {
        "fhir_server_status_code": 200,
        "fhir_server_response_body": {
            "entry": [],
            "resourceType": "Bundle",
            "type": "transaction-response",
        },
    }


@mock.patch("app.routers.fhir_transport_http.upload_bundle_to_fhir_server")
@mock.patch("app.routers.fhir_transport_http.credential_managers")
@mock.patch("app.routers.fhir_transport_http.AzureCredentialManager")
def test_upload_bundle_to_fhir_server_env_params_success(
    patched_azure_cred_manager, patched_cred_managers, patched_bundle_upload
):
    test_request = {
        "bundle": test_bundle,
    }

    patched_cred_managers.__getitem__.side_effect = {
        "azure": patched_azure_cred_manager
    }.__getitem__

    os.environ["CREDENTIAL_MANAGER"] = "azure"
    os.environ["FHIR_URL"] = "some-FHIR-server-URL"
    get_settings.cache_clear()

    fhir_server_response = mock.Mock()
    fhir_server_response.status_code = 200
    fhir_server_response.json.return_value = fhir_server_response_body
    patched_bundle_upload.return_value = fhir_server_response

    actual_response = client.post(
        "/fhir/transport/http/upload_bundle_to_fhir_server", json=test_request
    )

    patched_bundle_upload.assert_called_with(
        bundle=test_bundle,
        credential_manager=patched_azure_cred_manager,
        fhir_url="some-FHIR-server-URL",
    )
    assert actual_response.status_code == 200
    assert actual_response.json() == {
        "fhir_server_status_code": 200,
        "fhir_server_response_body": {
            "entry": [],
            "resourceType": "Bundle",
            "type": "transaction-response",
        },
    }


@mock.patch("app.routers.fhir_transport_http.upload_bundle_to_fhir_server")
@mock.patch("app.routers.fhir_transport_http.credential_managers")
@mock.patch("app.routers.fhir_transport_http.AzureCredentialManager")
def test_upload_bundle_to_fhir_server_missing_params(
    patched_azure_cred_manager, patched_cred_managers, patched_bundle_upload
):
    test_request = {
        "bundle": test_bundle,
    }

    os.environ.pop("CREDENTIAL_MANAGER", None)
    os.environ.pop("FHIR_URL", None)
    get_settings.cache_clear()

    fhir_server_response = mock.Mock()
    fhir_server_response.status_code = 200
    fhir_server_response.json.return_value = fhir_server_response_body
    patched_bundle_upload.return_value = fhir_server_response

    actual_response = client.post(
        "/fhir/transport/http/upload_bundle_to_fhir_server", json=test_request
    )
    assert ~patched_bundle_upload.called
    assert actual_response.status_code == 400
    assert actual_response.json() == (
        "The following values are required, but were not included in the request and "
        "could not be read from the environment. Please resubmit the request including "
        "these values or add them as environment variables to this service. missing "
        "values: credential_manager, fhir_url."
    )


@mock.patch("app.routers.fhir_transport_http.upload_bundle_to_fhir_server")
@mock.patch("app.routers.fhir_transport_http.credential_managers")
@mock.patch("app.routers.fhir_transport_http.AzureCredentialManager")
def test_upload_bundle_to_fhir_server_bad_response_from_server(
    patched_azure_cred_manager, patched_cred_managers, patched_bundle_upload
):
    test_request = {
        "bundle": test_bundle,
        "credential_manager": "azure",
        "fhir_url": "some-FHIR-server-URL",
    }

    fhir_server_response = mock.Mock()
    fhir_server_response.status_code = 400
    fhir_server_response.json.return_value = "some bad response from FHIR server"
    patched_bundle_upload.return_value = fhir_server_response

    actual_response = client.post(
        "/fhir/transport/http/upload_bundle_to_fhir_server", json=test_request
    )
    assert ~patched_bundle_upload.called
    assert actual_response.status_code == 400
    assert actual_response.json() == {
        "fhir_server_status_code": 400,
        "fhir_server_response_body": "some bad response from FHIR server",
    }


@mock.patch("app.routers.fhir_transport_http.upload_bundle_to_fhir_server")
@mock.patch("app.routers.fhir_transport_http.credential_managers")
@mock.patch("app.routers.fhir_transport_http.AzureCredentialManager")
def test_upload_bundle_to_fhir_server_partial_success(
    patched_azure_cred_manager, patched_cred_managers, patched_bundle_upload
):
    test_request = {
        "bundle": test_bundle,
        "credential_manager": "azure",
        "fhir_url": "some-FHIR-server-URL",
    }

    patched_cred_managers.__getitem__.side_effect = {
        "azure": patched_azure_cred_manager
    }.__getitem__

    partial_success_response_body = copy.deepcopy(fhir_server_response_body)
    partial_success_response_body["entry"][0]["response"]["status"] = "some issue"

    fhir_server_response = mock.Mock()
    fhir_server_response.status_code = 200
    fhir_server_response.json.return_value = partial_success_response_body
    patched_bundle_upload.return_value = fhir_server_response

    actual_response = client.post(
        "/fhir/transport/http/upload_bundle_to_fhir_server", json=test_request
    )

    patched_bundle_upload.assert_called_with(
        bundle=test_bundle,
        credential_manager=patched_azure_cred_manager,
        fhir_url=test_request["fhir_url"],
    )

    assert actual_response.status_code == 400
    assert actual_response.json() == {
        "fhir_server_status_code": 400,
        "fhir_server_response_body": {
            "entry": [
                {
                    "response": {
                        "etag": 'W/"MTY2Mjc0NTkxNDY4NTAxNTAwMA"',
                        "lastModified": "2022-09-09T17:51:54.685015+00:00",
                        "location": "https://somefhirstore.com",
                        "status": "some issue",
                    }
                }
            ],
            "resourceType": "Bundle",
            "type": "transaction-response",
        },
    }


@mock.patch("app.routers.fhir_transport_http.upload_bundle_to_fhir_server")
def test_upload_bundle_to_fhir_missing_bundle(patched_bundle_upload):

    test_request = {}

    actual_response = client.post(
        "/fhir/transport/http/upload_bundle_to_fhir_server", json=test_request
    )
    assert ~patched_bundle_upload.called
    assert actual_response.status_code == 422
    assert actual_response.json() == {
        "detail": [
            {
                "loc": ["body", "bundle"],
                "msg": "field required",
                "type": "value_error.missing",
            }
        ]
    }
