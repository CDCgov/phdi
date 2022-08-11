from .core import BaseCredentialManager
from azure.identity import DefaultAzureCredential


class AzureCredentialManager(BaseCredentialManager):
    """
    This class provides an Azure-specific credential manager.
    """

    def __init__(self, resource_location: str, scope: str):
        """
        Create a new BaseCredentialManager object.
        This object type is not intended to be called directly, but the constructor
        may be called from base classes.

        :param resource_location: URL or other location of the requested resource.
        :param scope: A space-delimited list of scopes to limit access to resource.
        """
        self.resource_location = resource_location
        self.scope = scope

    def get_credential_object(self):
        """
        Returns a cloud-specific credential object
        """
        return DefaultAzureCredential()

    def get_access_token(self, scope=None) -> str:
        """
        Obtain an access token from the Azure identity provider.

        :param scope: OAuth2 scope to request for the access token
        """
        creds = self.get_credential_object()

        if scope is None:
            # This is the value Azure expects in order to retrieve the default scope
            # from the identity provider
            scope = f"{self.resource_location}/.default"

        self.access_token = creds.get_token(scope)
        return self.access_token
