from .core import BaseCredentialManager
from azure.identity import DefaultAzureCredential


class AzureCredentialManager(BaseCredentialManager):
    """
    This class provides an Azure-specific credential manager.
    """

    @property
    def resource_location(self) -> str:
        return self.__resource_location

    @property
    def scope(self) -> str:
        return self.__scope

    def __init__(self, resource_location: str, scope: str = None):
        """
        Create a new AzureCredentialManager object.

        :param resource_location: URL or other location of the requested resource.
        :param scope: A space-delimited list of scopes to limit access to resource.
        """
        self.__resource_location = resource_location
        self.__scope = scope

        if self.scope is None:
            self.__scope = f"{self.resource_location}/.default"

    def get_credential_object(self) -> object:
        """
        Get an Azure-specific credential object.

        :return: Returns an instance of one of the *Credential objects from the
        `azure.identity` package.
        """
        return DefaultAzureCredential()

    def get_access_token(self) -> str:
        """
        Obtain an access token from the Azure identity provider.
        """
        creds = self.get_credential_object()

        self.access_token = creds.get_token(self.scope)
        return self.access_token
