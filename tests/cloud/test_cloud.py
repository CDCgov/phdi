import mock

from phdi.cloud.azure import AzureCredentialManager


@mock.patch("phdi.cloud.azure.DefaultAzureCredential")
def test_azure_credential_manager(mock_az_creds):

    # Setup mock data
    mock_az_creds_instance = mock_az_creds.return_value
    az_resource_location = "https://some-url"
    az_scope = "some-scope"
    az_access_token = mock.Mock(token="some-token")
    mock_az_creds_instance.get_token = mock.Mock(return_value=az_access_token)

    cred_manager = AzureCredentialManager(az_resource_location, az_scope)

    assert cred_manager.get_credential_object() == mock_az_creds_instance
    access_token = cred_manager.get_access_token()
    assert access_token == az_access_token

    # Test the default scope is used when called without the scope parameter
    mock_az_creds_instance.get_token.assert_called_with(
        f"{az_resource_location}/.default"
    )

    # Test the default scope is overridden when called with a scope parameter
    access_token = cred_manager.get_access_token(az_scope)
    mock_az_creds_instance.get_token.assert_called_with(az_scope)
