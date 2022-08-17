from datetime import datetime, timezone
from unittest import mock
from phdi.cloud.azure import AzureCredentialManager
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
