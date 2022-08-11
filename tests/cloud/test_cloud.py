from unittest import mock

from phdi.cloud.azure import AzureCredentialManager


@mock.patch("phdi.cloud.azure.DefaultAzureCredential")
def test_azure_credential_manager(mock_az_creds):

    mock_az_creds_instance = mock_az_creds.return_value
    az_resource_location = "https://some-url"
    az_scope = "some-scope"
    az_access_token = mock.Mock(token="some-token")
    mock_az_creds_instance.get_token = mock.Mock(return_value=az_access_token)

    cred_manager = AzureCredentialManager(az_resource_location, az_scope)

    assert cred_manager.get_credential_object() == mock_az_creds_instance
    access_token = cred_manager.get_access_token()
    assert access_token == az_access_token

    access_token = cred_manager.get_access_token()
    mock_az_creds_instance.get_token.assert_called_with(az_scope)


@mock.patch("phdi.cloud.azure.DefaultAzureCredential")
def test_azure_credential_manager_default_scope(mock_az_creds):

    mock_az_creds_instance = mock_az_creds.return_value
    az_resource_location = "https://some-url"
    az_access_token = mock.Mock(token="some-token")
    mock_az_creds_instance.get_token = mock.Mock(return_value=az_access_token)

    cred_manager = AzureCredentialManager(az_resource_location)

    assert cred_manager.get_credential_object() == mock_az_creds_instance
    access_token = cred_manager.get_access_token()
    assert access_token == az_access_token

    access_token = cred_manager.get_access_token()
    mock_az_creds_instance.get_token.assert_called_with(
        f"{az_resource_location}/.default"
    )
