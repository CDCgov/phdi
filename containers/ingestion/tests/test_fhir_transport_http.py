import copy
import json
import os
import pathlib
from unittest import mock

from app.config import get_settings
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

test_bundle = json.load(
    open(pathlib.Path(__file__).parent / "assets" / "single_patient_bundle.json")
)


fhir_server_response_body = json.load(
    open(pathlib.Path(__file__).parent / "assets" / "upload_response.json")
)


@mock.patch("app.routers.fhir_transport_http.upload_bundle_to_fhir_server")
@mock.patch("app.routers.fhir_transport_http.get_cred_manager")
def test_upload_bundle_to_fhir_server_request_params_success(
    patched_azure_cred_manager, patched_bundle_upload
):
    manager = "azure"
    fhir_url = "some-FHIR-server-URL"
    test_request = {
        "bundle": test_bundle,
        "cred_manager": manager,
        "fhir_url": fhir_url,
    }

    patched_azure_cred_manager.return_value = mock.Mock()

    fhir_server_response = [mock.Mock()]
    fhir_server_response[0].status_code = 200
    fhir_server_response[0].json.return_value = fhir_server_response_body
    patched_bundle_upload.return_value = fhir_server_response

    actual_response = client.post(
        "/fhir/transport/http/upload_bundle_to_fhir_server", json=test_request
    )

    patched_bundle_upload.assert_called_with(
        bundle=test_bundle,
        cred_manager=patched_azure_cred_manager(),
        fhir_url=test_request["fhir_url"],
    )
    assert actual_response.status_code == 200
    assert actual_response.json() == {
        "status_code": "200",
        "message": {
            "fhir_server_response": {
                "fhir_server_status_code": [200],
                "fhir_server_response_body": {
                    "entry": [],
                    "resourceType": "Bundle",
                    "type": "transaction-response",
                },
            }
        },
        "bundle": None,
    }


@mock.patch("app.routers.fhir_transport_http.upload_bundle_to_fhir_server")
@mock.patch("app.routers.fhir_transport_http.get_cred_manager")
def test_upload_bundle_to_fhir_server_env_params_success(
    patched_azure_cred_manager, patched_bundle_upload
):
    test_request = {
        "bundle": test_bundle,
    }

    patched_azure_cred_manager.return_value = mock.Mock()

    os.environ["CRED_MANAGER"] = "azure"
    os.environ["FHIR_URL"] = "some-FHIR-server-URL"
    get_settings.cache_clear()

    fhir_server_response = [mock.Mock()]
    fhir_server_response[0].status_code = 200
    fhir_server_response[0].json.return_value = fhir_server_response_body
    patched_bundle_upload.return_value = fhir_server_response

    actual_response = client.post(
        "/fhir/transport/http/upload_bundle_to_fhir_server", json=test_request
    )

    patched_bundle_upload.assert_called_with(
        bundle=test_bundle,
        cred_manager=patched_azure_cred_manager(),
        fhir_url="some-FHIR-server-URL",
    )
    os.environ.pop("CRED_MANAGER", None)
    os.environ.pop("FHIR_URL", None)

    assert actual_response.status_code == 200
    assert actual_response.json() == {
        "status_code": "200",
        "message": {
            "fhir_server_response": {
                "fhir_server_status_code": [200],
                "fhir_server_response_body": {
                    "entry": [],
                    "resourceType": "Bundle",
                    "type": "transaction-response",
                },
            }
        },
        "bundle": None,
    }


@mock.patch("app.routers.fhir_transport_http.upload_bundle_to_fhir_server")
@mock.patch("app.routers.fhir_transport_http.get_cred_manager")
def test_upload_bundle_to_fhir_server_missing_params(
    patched_azure_cred_manager, patched_bundle_upload
):
    test_request = {
        "bundle": test_bundle,
    }

    os.environ.pop("CRED_MANAGER", None)
    os.environ.pop("FHIR_URL", None)
    get_settings.cache_clear()

    patched_azure_cred_manager.return_value = mock.Mock()

    fhir_server_response = mock.Mock()
    fhir_server_response.status_code = 200
    fhir_server_response.json.return_value = fhir_server_response_body
    patched_bundle_upload.return_value = fhir_server_response

    actual_response = client.post(
        "/fhir/transport/http/upload_bundle_to_fhir_server", json=test_request
    )
    expected_message = (
        "The following values are required, but were not included in the request and "
        "could not be read from the environment. Please resubmit the request including "
        "these values or add them as environment variables to this service. missing "
        "values: cred_manager, fhir_url."
    )
    expected_response = {
        "status_code": "400",
        "message": expected_message,
        "bundle": None,
    }
    assert ~patched_bundle_upload.called
    assert actual_response.status_code == 400
    assert actual_response.json() == expected_response


@mock.patch("app.routers.fhir_transport_http.upload_bundle_to_fhir_server")
@mock.patch("app.routers.fhir_transport_http.get_cred_manager")
def test_upload_bundle_to_fhir_server_bad_response_from_server(
    patched_azure_cred_manager, patched_bundle_upload
):
    test_request = {
        "bundle": test_bundle,
        "cred_manager": "azure",
        "fhir_url": "some-FHIR-server-URL",
    }

    patched_azure_cred_manager.return_value = mock.Mock()

    fhir_server_response = [mock.Mock()]
    fhir_server_response[0].status_code = 400
    patched_bundle_upload.return_value = fhir_server_response

    actual_response = client.post(
        "/fhir/transport/http/upload_bundle_to_fhir_server", json=test_request
    )
    assert ~patched_bundle_upload.called
    assert actual_response.status_code == 400
    assert actual_response.json() == {
        "status_code": "400",
        "message": {
            "fhir_server_response": {
                "fhir_server_status_code": [400],
                "fhir_server_response_body": {
                    "entry": [],
                    "resourceType": "Bundle",
                    "type": "transaction-response",
                },
            }
        },
        "bundle": None,
    }


@mock.patch("app.routers.fhir_transport_http.upload_bundle_to_fhir_server")
@mock.patch("app.routers.fhir_transport_http.get_cred_manager")
def test_upload_bundle_to_fhir_server_partial_success(
    patched_azure_cred_manager, patched_bundle_upload
):
    test_request = {
        "bundle": test_bundle,
        "cred_manager": "azure",
        "fhir_url": "some-FHIR-server-URL",
    }

    patched_azure_cred_manager.return_value = mock.Mock()

    partial_success_response_body = copy.deepcopy(fhir_server_response_body)
    partial_success_response_body["entry"][0]["response"]["status"] = "some issue"

    fhir_server_response = [mock.Mock()]
    fhir_server_response[0].status_code = 200
    fhir_server_response[0].json.return_value = partial_success_response_body
    patched_bundle_upload.return_value = fhir_server_response

    actual_response = client.post(
        "/fhir/transport/http/upload_bundle_to_fhir_server", json=test_request
    )

    patched_bundle_upload.assert_called_with(
        bundle=test_bundle,
        cred_manager=patched_azure_cred_manager(),
        fhir_url=test_request["fhir_url"],
    )
    assert actual_response.status_code == 400
    assert actual_response.json() == {
        "status_code": "400",
        "message": {
            "fhir_server_response": {
                "fhir_server_status_code": [200],
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
        },
        "bundle": None,
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


@mock.patch("app.routers.fhir_transport_http.upload_bundle_to_fhir_server")
@mock.patch("app.routers.fhir_transport_http.get_cred_manager")
def test_upload_bundle_to_fhir_server_request_params_success_500(
    patched_azure_cred_manager, patched_bundle_upload
):
    bundle = json.load(
        open(
            pathlib.Path(__file__).parent
            / "assets"
            / "example_eicr_with_rr_data_with_person.json"
        )
    )
    single_resource = bundle.get("entry")[0]
    # add 500 resources to bundle and then pass to function
    for x in range(500):
        bundle["entry"].append(single_resource)

    my_count = len(bundle.get("entry"))
    assert my_count == 545
    manager = "azure"
    fhir_url = "some-FHIR-server-URL"
    test_request = {
        "bundle": bundle,
        "cred_manager": manager,
        "fhir_url": fhir_url,
    }

    patched_azure_cred_manager.return_value = mock.Mock()

    fhir_server_response = [mock.Mock(), mock.Mock()]
    fhir_server_response[0].status_code = 200
    fhir_server_response[0].json.return_value = fhir_server_response_body
    fhir_server_response[1].status_code = 200
    fhir_server_response[1].json.return_value = fhir_server_response_body
    patched_bundle_upload.return_value = fhir_server_response

    actual_response = client.post(
        "/fhir/transport/http/upload_bundle_to_fhir_server", json=test_request
    )

    patched_bundle_upload.assert_called_with(
        bundle=bundle,
        cred_manager=patched_azure_cred_manager(),
        fhir_url=test_request["fhir_url"],
    )
    assert actual_response.status_code == 200
    assert actual_response.json() == {
        "status_code": "200",
        "message": {
            "fhir_server_response": {
                "fhir_server_status_code": [200, 200],
                "fhir_server_response_body": {
                    "entry": [],
                    "resourceType": "Bundle",
                    "type": "transaction-response",
                },
            }
        },
        "bundle": None,
    }


@mock.patch("app.routers.fhir_transport_http.upload_bundle_to_fhir_server")
@mock.patch("app.routers.fhir_transport_http.get_cred_manager")
def test_upload_bundle_to_fhir_server_partial_success_500(
    patched_azure_cred_manager, patched_bundle_upload
):
    bundle = json.load(
        open(
            pathlib.Path(__file__).parent
            / "assets"
            / "example_eicr_with_rr_data_with_person.json"
        )
    )
    single_resource = bundle.get("entry")[0]
    # add 500 resources to bundle and then pass to function
    for x in range(500):
        bundle["entry"].append(single_resource)

    my_count = len(bundle.get("entry"))
    assert my_count == 545
    test_request = {
        "bundle": bundle,
        "cred_manager": "azure",
        "fhir_url": "some-FHIR-server-URL",
    }

    patched_azure_cred_manager.return_value = mock.Mock()

    partial_success_response_body = copy.deepcopy(fhir_server_response_body)
    partial_success_response_body["entry"][0]["response"]["status"] = "some issue"

    fhir_server_response = [mock.Mock(), mock.Mock()]
    fhir_server_response[0].status_code = 200
    fhir_server_response[0].json.return_value = partial_success_response_body
    fhir_server_response[1].status_code = 400
    fhir_server_response[1].json.return_value = partial_success_response_body
    patched_bundle_upload.return_value = fhir_server_response

    actual_response = client.post(
        "/fhir/transport/http/upload_bundle_to_fhir_server", json=test_request
    )

    patched_bundle_upload.assert_called_with(
        bundle=bundle,
        cred_manager=patched_azure_cred_manager(),
        fhir_url=test_request["fhir_url"],
    )
    assert actual_response.status_code == 400
    assert actual_response.json() == {
        "status_code": "400",
        "message": {
            "fhir_server_response": {
                "fhir_server_status_code": [200, 400],
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
        },
        "bundle": None,
    }
