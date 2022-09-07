import json
import pathlib
import pytest

from datetime import datetime, timezone
from unittest import mock
from phdi.cloud.azure import (
    AzureCredentialManager,
    AzureCloudContainerConnection,
)
from phdi.cloud.gcp import GcpCredentialManager


@mock.patch("phdi.cloud.azure.DefaultAzureCredential")
def test_azure_credential_manager(mock_az_creds):

    mock_az_creds_instance = mock_az_creds.return_value
    az_resource_location = "https://some-url"
    az_scope = "some-scope"
    az_access_token_str = "some-token"
    az_access_token_exp = datetime.now(timezone.utc).timestamp() + 1000
    az_access_token = mock.Mock(
        token=az_access_token_str, expires_on=az_access_token_exp
    )
    mock_az_creds_instance.get_token = mock.Mock(return_value=az_access_token)

    cred_manager = AzureCredentialManager(az_resource_location, az_scope)

    assert cred_manager.get_credential_object() == mock_az_creds_instance
    access_token = cred_manager.get_access_token()
    assert access_token == az_access_token_str

    access_token = cred_manager.get_access_token()
    mock_az_creds_instance.get_token.assert_called_with(az_scope)
    assert access_token == az_access_token_str


@mock.patch("phdi.cloud.azure.DefaultAzureCredential")
def test_azure_credential_manager_default_scope(mock_az_creds):

    mock_az_creds_instance = mock_az_creds.return_value
    az_resource_location = "https://some-url"

    az_access_token_str = "some-token"
    az_access_token_exp = datetime.now(timezone.utc).timestamp() + 1000
    az_access_token = mock.Mock(
        token=az_access_token_str, expires_on=az_access_token_exp
    )
    mock_az_creds_instance.get_token = mock.Mock(return_value=az_access_token)

    cred_manager = AzureCredentialManager(az_resource_location)

    assert cred_manager.get_credential_object() == mock_az_creds_instance
    access_token = cred_manager.get_access_token()
    assert access_token == az_access_token_str

    access_token = cred_manager.get_access_token()
    mock_az_creds_instance.get_token.assert_called_with(
        f"{az_resource_location}/.default"
    )
    assert access_token == az_access_token_str


@mock.patch("phdi.cloud.azure.DefaultAzureCredential")
def test_azure_credential_manager_reuse_token(mock_az_creds):

    mock_az_creds_instance = mock_az_creds.return_value
    az_resource_location = "https://some-url"

    az_access_token_str1 = "some-token1"
    az_access_token_exp1 = datetime.now(timezone.utc).timestamp() + 1000
    az_access_token1 = mock.Mock(
        token=az_access_token_str1, expires_on=az_access_token_exp1
    )
    az_access_token_str2 = "some-token2"
    az_access_token_exp2 = datetime.now(timezone.utc).timestamp() + 1000
    az_access_token2 = mock.Mock(
        token=az_access_token_str2, expires_on=az_access_token_exp2
    )
    mock_az_creds_instance.get_token = mock.Mock(
        side_effect=[az_access_token1, az_access_token2]
    )

    cred_manager = AzureCredentialManager(az_resource_location)

    assert cred_manager.get_credential_object() == mock_az_creds_instance
    access_token = cred_manager.get_access_token()
    assert access_token == az_access_token_str1

    access_token = cred_manager.get_access_token()
    mock_az_creds_instance.get_token.assert_called_with(
        f"{az_resource_location}/.default"
    )
    assert access_token == az_access_token_str1


@mock.patch("phdi.cloud.azure.DefaultAzureCredential")
def test_azure_credential_manager_refresh_token(mock_az_creds):

    mock_az_creds_instance = mock_az_creds.return_value
    az_resource_location = "https://some-url"

    az_access_token_str1 = "some-token1"
    az_access_token_exp1 = datetime.now(timezone.utc).timestamp() - 1000
    az_access_token1 = mock.Mock(
        token=az_access_token_str1, expires_on=az_access_token_exp1
    )
    az_access_token_str2 = "some-token2"
    az_access_token_exp2 = datetime.now(timezone.utc).timestamp() + 1000
    az_access_token2 = mock.Mock(
        token=az_access_token_str2, expires_on=az_access_token_exp2
    )
    mock_az_creds_instance.get_token = mock.Mock(
        side_effect=[az_access_token1, az_access_token2]
    )

    cred_manager = AzureCredentialManager(az_resource_location)

    assert cred_manager.get_credential_object() == mock_az_creds_instance
    access_token = cred_manager.get_access_token()
    assert access_token == az_access_token_str1

    access_token = cred_manager.get_access_token()
    mock_az_creds_instance.get_token.assert_called_with(
        f"{az_resource_location}/.default"
    )
    assert access_token == az_access_token_str2


@mock.patch("phdi.cloud.azure.DefaultAzureCredential")
def test_azure_credential_manager_force_refresh_token(mock_az_creds):

    mock_az_creds_instance = mock_az_creds.return_value
    az_resource_location = "https://some-url"

    az_access_token_str1 = "some-token1"
    az_access_token_exp1 = datetime.now(timezone.utc).timestamp() + 1000
    az_access_token1 = mock.Mock(
        token=az_access_token_str1, expires_on=az_access_token_exp1
    )
    az_access_token_str2 = "some-token2"
    az_access_token_exp2 = datetime.now(timezone.utc).timestamp() + 1000
    az_access_token2 = mock.Mock(
        token=az_access_token_str2, expires_on=az_access_token_exp2
    )
    mock_az_creds_instance.get_token = mock.Mock(
        side_effect=[az_access_token1, az_access_token2]
    )

    cred_manager = AzureCredentialManager(az_resource_location)

    assert cred_manager.get_credential_object() == mock_az_creds_instance
    access_token = cred_manager.get_access_token()
    assert access_token == az_access_token_str1

    access_token = cred_manager.get_access_token(force_refresh=True)
    mock_az_creds_instance.get_token.assert_called_with(
        f"{az_resource_location}/.default"
    )
    assert access_token == az_access_token_str2


@mock.patch("phdi.cloud.gcp.google.auth.transport.requests.Request")
@mock.patch("phdi.cloud.gcp.google.auth.default")
def test_gcp_credential_manager(mock_gcp_creds, mock_gcp_requests):

    # Set dummy project ID, access token, and scope values.
    project_id = "some-project"
    token = "some-token"
    scope = ["some-scope"]

    # Make dummy GCP credentials object.
    credentials = mock.Mock()
    credentials.token = token
    credentials.expired = False
    credentials.valid = True

    mock_gcp_creds.return_value = credentials, project_id

    credential_manager = GcpCredentialManager(scope=scope)

    assert credential_manager.get_access_token() == token
    assert credential_manager.get_project_id() == project_id
    mock_gcp_creds.assert_called_with(scopes=scope)

    # Test that making additional access token requests does not result in calls to GCP
    # when the creds are not expired and the token is valid.
    _ = credential_manager.get_access_token()
    _ = credential_manager.get_project_id()
    assert mock_gcp_creds.call_count == 1
    assert mock_gcp_requests.not_called


@mock.patch("phdi.cloud.gcp.google.auth.transport.requests.Request")
@mock.patch("phdi.cloud.gcp.google.auth.default")
def test_gcp_credential_manager_handle_expired_token(mock_gcp_creds, mock_gcp_requests):

    # Set dummy project ID, access token, and scope values.
    project_id = "some-project"
    token = "some-token"
    scope = ["some-scope"]

    # Make dummy GCP credentials object.
    credentials = mock.Mock()
    credentials.token = token
    credentials.expired = False
    credentials.valid = False

    mock_gcp_creds.return_value = credentials, project_id

    credential_manager = GcpCredentialManager(scope=scope)

    # When invalid credentials are encountered they should be refreshed by the
    # credential manager when a new token is requested.
    _ = credential_manager.get_credential_object()
    _ = credential_manager.get_access_token()
    assert mock_gcp_requests.called


@mock.patch("phdi.cloud.gcp.google.auth.default")
def test_gcp_credential_manager_handle_expired_credentials(
    mock_gcp_creds,
):

    # Set dummy project ID, access token, and scope values.
    project_id = "some-project"
    token = "some-token"
    scope = ["some-scope"]

    # Make dummy GCP credentials object.
    credentials = mock.Mock()
    credentials.token = token
    credentials.expired = True
    credentials.valid = False

    mock_gcp_creds.return_value = credentials, project_id

    credential_manager = GcpCredentialManager(scope=scope)

    # When expired credentials are encountered they should be replaced by the
    # credential manager when a new token is requested.
    _ = credential_manager.get_credential_object()
    _ = credential_manager.get_access_token()
    assert mock_gcp_creds.call_count == 2


@mock.patch.object(AzureCloudContainerConnection, "_get_container_client")
def test_upload_object(mock_get_client):
    mock_blob_client = mock.Mock()

    mock_container_client = mock.Mock()
    mock_container_client.get_blob_client.return_value = mock_blob_client

    mock_get_client.return_value = mock_container_client

    mock_cred_manager = mock.Mock()

    object_storage_account = "some-resource-location"
    phdi_container_client = AzureCloudContainerConnection(
        object_storage_account, mock_cred_manager
    )
    object_container = "some-container"
    object_path = "output/path/some-bundle-type/some-filename-1.fhir"

    # Test both cases of input data types
    object_content_json = {"hello": "world"}
    object_content_str = "hello world"

    phdi_container_client.upload_object(
        object_content_json,
        object_container,
        object_path,
    )
    mock_container_client.get_blob_client.assert_called_with(object_path)
    mock_blob_client.upload_blob.assert_called_with(
        json.dumps(object_content_json).encode("utf-8"), overwrite=True
    )

    phdi_container_client.upload_object(
        object_content_str,
        object_container,
        object_path,
    )
    mock_blob_client.upload_blob.assert_called_with(
        bytes(object_content_str, "utf-8"), overwrite=True
    )


@mock.patch.object(AzureCloudContainerConnection, "_get_container_client")
def test_download_object(mock_get_client):
    mock_blob_client = mock.Mock()

    mock_container_client = mock.Mock()
    mock_container_client.get_blob_client.return_value = mock_blob_client

    mock_get_client.return_value = mock_container_client

    mock_cred_manager = mock.Mock()

    object_storage_account = "some-resource-location"
    object_container = "some-container"
    object_path = "output/path/some-bundle-type/some-filename-1.fhir"
    object_content = {"hello": "world"}

    mock_downloader = mock.Mock(
        content_as_text=lambda encoding: json.dumps(object_content)
    )
    mock_blob_client.download_blob.return_value = mock_downloader

    phdi_container_client = AzureCloudContainerConnection(
        object_storage_account, mock_cred_manager
    )

    download_content = phdi_container_client.download_object(
        object_container,
        object_path,
    )

    assert json.loads(download_content) == object_content

    mock_container_client.get_blob_client.assert_called_with(object_path)

    mock_blob_client.download_blob.assert_called_with()


@mock.patch.object(AzureCloudContainerConnection, "_get_container_client")
def test_download_object_cp1252(mock_get_client):
    mock_blob_client = mock.Mock()

    mock_container_client = mock.Mock()
    mock_container_client.get_blob_client.return_value = mock_blob_client

    mock_get_client.return_value = mock_container_client

    mock_cred_manager = mock.Mock()

    object_storage_account = "some-resource-location"
    object_container = "some-container"
    object_path = "output/path/some-bundle-type/some-filename-1.fhir"

    with open(
        pathlib.Path(__file__).parent.parent / "assets" / "cp1252-sample.txt", "rb"
    ) as cp1252file:
        object_content = cp1252file.read()

    mock_downloader = mock.Mock(
        content_as_text=lambda encoding: object_content.decode(encoding=encoding)
    )

    mock_blob_client.download_blob.return_value = mock_downloader

    phdi_container_client = AzureCloudContainerConnection(
        object_storage_account,
        mock_cred_manager,
    )

    download_content = phdi_container_client.download_object(
        object_container, object_path, "cp1252"
    )

    assert download_content == "Testing windows-1252 encoding\n€\nœ\nŸ\n"

    with pytest.raises(UnicodeDecodeError):
        object_content.decode("utf-8")

    mock_container_client.get_blob_client.assert_called_with(object_path)

    mock_blob_client.download_blob.assert_called_with()


@mock.patch("phdi.cloud.azure.BlobServiceClient")
def test_list_containers(mock_service_client):
    mock_service_client_instance = mock_service_client.return_value
    item1 = mock.Mock()
    item1.name = "container1"
    item2 = mock.Mock()
    item2.name = "container2"
    mock_container_list = [item1, item2]

    mock_service_client_instance.list_containers.return_value = mock_container_list

    mock_cred_manager = mock.Mock()

    object_storage_account = "some-resource-location"

    phdi_container_client = AzureCloudContainerConnection(
        object_storage_account, mock_cred_manager
    )

    container_list = phdi_container_client.list_containers()

    mock_service_client.assert_called_with(
        account_url=object_storage_account,
        credential=mock_cred_manager.get_credential_object(),
    )

    mock_service_client_instance.list_containers.assert_called_with()

    assert container_list == ["container1", "container2"]


@mock.patch.object(AzureCloudContainerConnection, "_get_container_client")
def test_list_objects(mock_get_client):
    item1 = mock.Mock()
    item1.name = "blob1"
    item2 = mock.Mock()
    item2.name = "blob2"
    mock_object_list = [item1, item2]

    mock_client = mock_get_client.return_value

    mock_client.list_blobs.return_value = mock_object_list

    object_storage_account = "some-resource-location"
    object_container = "some-container-name"
    object_prefix = "some-prefix"

    mock_cred_manager = mock.Mock()

    phdi_container_client = AzureCloudContainerConnection(
        object_storage_account, mock_cred_manager
    )

    blob_list = phdi_container_client.list_objects(object_container, object_prefix)

    mock_get_client.assert_called_with(f"{object_storage_account}/{object_container}")

    mock_client.list_blobs.assert_called_with(name_starts_with=object_prefix)

    assert blob_list == ["blob1", "blob2"]
