import io
import json
import pathlib
from datetime import datetime
from datetime import timezone
from unittest import mock

import pytest
from azure.storage.blob import ContainerClient

from phdi.cloud.azure import AzureCloudContainerConnection
from phdi.cloud.azure import AzureCredentialManager
from phdi.cloud.gcp import GcpCloudStorageConnection
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


def test_azure_need_new_token_without_token():
    cred_manager = AzureCredentialManager("https://some-url")
    assert cred_manager._need_new_token()


@mock.patch("phdi.cloud.azure.SecretClient")
@mock.patch("phdi.cloud.azure.DefaultAzureCredential")
def test_azure_credential_manager_get_secret(
    patched_az_creds, patched_az_secret_client
):
    # Set dummy values for key vault name and secret name.
    key_vault_name = "some-key-vault"
    secret_name = "some-secret"

    # Mock SecretClient with appropriate return value.
    secret_object = mock.Mock()
    secret_object.value = "some-secret-value"
    secret_client = mock.Mock()
    secret_client.get_secret.return_value = secret_object
    patched_az_secret_client.return_value = secret_client
    cred_manager = AzureCredentialManager()
    assert cred_manager.get_secret(key_vault_name, secret_name) == secret_object.value


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

    # Make dummy GCP credentials object.
    credentials = mock.Mock()
    credentials.token = token
    credentials.expired = False
    credentials.valid = False

    mock_gcp_creds.return_value = credentials, project_id

    credential_manager = GcpCredentialManager()

    # When invalid credentials are encountered they should be refreshed by the
    # credential manager when a new token is requested.
    assert credential_manager.get_project_id() is not None
    scoped_credentials = credential_manager.get_credential_object()
    assert scoped_credentials == credential_manager.scoped_credentials
    assert credential_manager.project_id is not None
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


@mock.patch.object(ContainerClient, "from_container_url")
def test_azure_upload_object(mock_get_client):
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
def test_azure_download_object(mock_get_client):
    mock_blob_client = mock.Mock()

    mock_container_client = mock.Mock()
    mock_container_client.get_blob_client.return_value = mock_blob_client

    mock_get_client.return_value = mock_container_client

    mock_cred_manager = mock.Mock()

    object_storage_account = "some-resource-location"
    object_container = "some-container"
    object_path = "output/path/some-bundle-type/some-filename-1.fhir"
    object_content = {"hello": "world"}

    mock_downloader = mock.Mock()
    mock_downloader.readall.return_value = json.dumps(object_content).encode("utf-8")
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

    mock_blob_client.download_blob.assert_called_with(encoding="UTF-8")


@mock.patch.object(AzureCloudContainerConnection, "_get_container_client")
def test_azure_download_object_cp1252(mock_get_client):
    mock_blob_client = mock.Mock()

    mock_container_client = mock.Mock()
    mock_container_client.get_blob_client.return_value = mock_blob_client

    mock_get_client.return_value = mock_container_client

    mock_cred_manager = mock.Mock()

    object_storage_account = "some-resource-location"
    object_container = "some-container"
    object_path = "output/path/some-bundle-type/some-filename-1.fhir"

    with open(
        pathlib.Path(__file__).parent.parent / "assets" / "cloud" / "cp1252-sample.txt",
        "rb",
    ) as cp1252file:
        object_content = cp1252file.read()

    mock_downloader = mock.Mock()
    mock_downloader.readall.return_value = object_content.decode("cp1252")

    mock_blob_client.download_blob.return_value = mock_downloader

    phdi_container_client = AzureCloudContainerConnection(
        object_storage_account,
        mock_cred_manager,
    )

    download_content = phdi_container_client.download_object(
        object_container, object_path, "cp1252"
    )
    download_content_buffer = io.StringIO(download_content)

    assert download_content_buffer.readline() == "Testing windows-1252 encoding € œ Ÿ"

    with pytest.raises(UnicodeDecodeError):
        object_content.decode("utf-8")

    mock_container_client.get_blob_client.assert_called_with(object_path)

    mock_blob_client.download_blob.assert_called_with(encoding="cp1252")


@mock.patch("phdi.cloud.azure.BlobServiceClient")
def test_azure_list_containers(mock_service_client):
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
def test_azure_list_objects(mock_get_client):
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


@mock.patch.object(AzureCloudContainerConnection, "_get_container_client")
def test_azure_blob_exists(mock_get_client):
    mocked_blob_client = mock.Mock()
    mocked_blob_client.exists.return_value = True

    mocked_container_client = mock.Mock()
    mocked_container_client.get_blob_client.return_value = mocked_blob_client

    mock_get_client.return_value = mocked_container_client

    object_storage_account = "some-resource-location"
    object_container = "some-container-name"
    filename = "some-file-name"

    mock_cred_manager = mock.Mock()

    phdi_container_client = AzureCloudContainerConnection(
        object_storage_account, mock_cred_manager
    )

    exists = phdi_container_client.blob_exists(object_container, filename)

    mock_get_client.assert_called_with(f"{object_storage_account}/{object_container}")
    mocked_container_client.get_blob_client.assert_called_with(filename)
    mocked_blob_client.exists.assert_called()
    assert exists is True


def test_gcp_storage_connect_init():
    phdi_container_client = GcpCloudStorageConnection()
    assert phdi_container_client._GcpCloudStorageConnection__storage_client is None


@mock.patch("phdi.cloud.gcp.storage")
def test_gcp_get_storage_client(patched_storage):
    phdi_container_client = GcpCloudStorageConnection()
    phdi_container_client._get_storage_client()
    assert patched_storage.Client.called


@mock.patch.object(GcpCloudStorageConnection, "_get_storage_client")
def test_gcp_upload_object(mock_get_client):
    mock_blob = mock.Mock()
    mock_bucket = mock.Mock()

    mock_storage_client = mock.Mock()
    mock_storage_client.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    mock_get_client.return_value = mock_storage_client

    phdi_container_client = GcpCloudStorageConnection()

    object_bucket = "some-container"
    object_path = "output/path/some-bundle-type/some-filename-1.fhir"

    object_content_str = "hello world"

    phdi_container_client.upload_object(
        object_content_str,
        object_bucket,
        object_path,
    )
    mock_storage_client.bucket.assert_called_with(object_bucket)
    mock_blob.upload_from_string.assert_called_with(
        data=object_content_str,
        content_type="application/json",
    )


@mock.patch.object(GcpCloudStorageConnection, "_get_storage_client")
def test_gcp_download_object(mock_get_client):
    mock_blob = mock.Mock()
    mock_bucket = mock.Mock()

    mock_storage_client = mock.Mock()
    mock_storage_client.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    mock_get_client.return_value = mock_storage_client

    object_bucket = "some-container"
    object_path = "output/path/some-bundle-type/some-filename-1.fhir"
    object_content = {"hello": "world"}

    mock_blob.download_as_text.return_value = json.dumps(object_content)

    phdi_container_client = GcpCloudStorageConnection()
    download_content = phdi_container_client.download_object(
        object_bucket,
        object_path,
    )

    assert json.loads(download_content) == object_content

    mock_storage_client.bucket.assert_called_with(object_bucket)

    mock_blob.download_as_text.assert_called_with(encoding="utf-8")


@mock.patch.object(GcpCloudStorageConnection, "_get_storage_client")
def test_gcp_list_objects(mock_get_client):
    item1 = mock.Mock()
    item1.name = "blob1"
    item2 = mock.Mock()
    item2.name = "blob2"
    mock_object_list = [item1, item2]

    mock_storage_client = mock.Mock()
    mock_get_client.return_value = mock_storage_client
    mock_storage_client.list_blobs.return_value = mock_object_list

    object_bucket = "some-container"
    phdi_storage_client = GcpCloudStorageConnection()
    blob_list = phdi_storage_client.list_objects(object_bucket)

    mock_storage_client.list_blobs.assert_called_with(object_bucket, prefix="")
    assert blob_list == ["blob1", "blob2"]


@mock.patch.object(GcpCloudStorageConnection, "_get_storage_client")
def test_gcp_list_containers(mock_get_client):
    item1 = "blob1"
    item2 = "blob2"
    mock_bucket_list = [item1, item2]

    mock_storage_client = mock.Mock()
    mock_get_client.return_value = mock_storage_client
    mock_storage_client.list_buckets.return_value = mock_bucket_list

    phdi_storage_client = GcpCloudStorageConnection()
    bucket_list = phdi_storage_client.list_containers()

    mock_storage_client.list_buckets.assert_called_with()

    assert bucket_list == ["blob1", "blob2"]
