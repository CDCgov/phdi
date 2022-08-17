from datetime import datetime, timezone
from unittest import mock
from phdi.cloud.azure import AzureCredentialManager


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
