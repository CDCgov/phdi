from datetime import datetime, timezone
import os

from unittest import mock

from IntakePipeline.fhir import (
    store_data,
    get_fhirserver_cred_manager,
    upload_bundle_to_fhir_server,
)

from azure.identity import DefaultAzureCredential


@mock.patch("IntakePipeline.fhir.get_blob_client")
def test_store_bundle(mock_get_client):
    mock_blob = mock.Mock()

    mock_client = mock.Mock()
    mock_client.get_blob_client.return_value = mock_blob

    mock_get_client.return_value = mock_client

    store_data(
        "some-url",
        "output/path",
        "some-filename-1.fhir",
        "some-bundle-type",
        {"hello": "world"},
    )

    mock_client.get_blob_client.assert_called_with(
        os.path.normpath("output/path/some-bundle-type/some-filename-1.fhir")
    )
    mock_blob.upload_blob.assert_called()


@mock.patch("requests.post")
def test_upload_bundle_to_fhir_server(mock_fhir_post):

    mock_fhirserver_cred_manager = mock.Mock()
    mock_fhirserver_cred_manager.fhir_url = "https://fhir-url"

    # Create a mock token
    mock_access_token = mock.Mock()
    mock_access_token.token = "my-token"
    mock_access_token.expires_on = datetime.now(timezone.utc).timestamp() + 2399
    mock_fhirserver_cred_manager.get_access_token.return_value = mock_access_token

    upload_bundle_to_fhir_server(
        mock_fhirserver_cred_manager,
        {
            "resourceType": "Bundle",
            "id": "some-id",
            "entry": [
                {
                    "resource": {"resourceType": "Patient", "id": "pat-id"},
                    "request": {"method": "PUT", "url": "Patient/pat-id"},
                }
            ],
        },
    )

    mock_fhir_post.assert_called_with(
        "https://fhir-url",
        headers={
            "Authorization": "Bearer my-token",
            "Accept": "application/fhir+json",
            "Content-Type": "application/fhir+json",
        },
        data='{"resourceType": "Bundle", "id": "some-id", "entry": [{"resource": '
        '{"resourceType": "Patient", "id": "pat-id"}, "request": '
        '{"method": "PUT", "url": "Patient/pat-id"}}]}',
    )


@mock.patch.object(DefaultAzureCredential, "get_token")
def test_get_access_token_reuse(mock_get_token):

    mock_access_token = mock.Mock()
    mock_access_token.token = "my-token"
    mock_access_token.expires_on = datetime.now(timezone.utc).timestamp() + 2399

    mock_get_token.return_value = mock_access_token

    fhirserver_cred_manager = get_fhirserver_cred_manager("https://fhir-url")
    token1 = fhirserver_cred_manager.get_access_token()

    # Use the default token reuse tolerance, which is less than
    # the mock token's time to live of 2399
    fhirserver_cred_manager.get_access_token()
    mock_get_token.assert_called_once_with("https://fhir-url/.default")
    assert token1.token == "my-token"


@mock.patch.object(DefaultAzureCredential, "get_token")
def test_get_access_token_refresh(mock_get_token):

    mock_access_token = mock.Mock()
    mock_access_token.token = "my-token"
    mock_access_token.expires_on = datetime.now(timezone.utc).timestamp() + 2399

    mock_get_token.return_value = mock_access_token

    fhirserver_cred_manager = get_fhirserver_cred_manager("https://fhir-url")
    token1 = fhirserver_cred_manager.get_access_token()

    # This time, use a very high token reuse tolerance to
    # force another refresh for the new call
    fhirserver_cred_manager.get_access_token(2500)
    mock_get_token.assert_has_calls(
        [mock.call("https://fhir-url/.default"), mock.call("https://fhir-url/.default")]
    )
    assert token1.token == "my-token"
