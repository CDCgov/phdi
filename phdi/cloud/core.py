from abc import ABC, abstractmethod


class BaseCredentialManager(ABC):
    """
    This class is intended to provide a common interface for managing service
    credentials.
    """

    def __init__(self, resource_location: str, scope: str = None):
        """
        Create a new BaseCredentialManager object.
        This object type is not intended to be called directly, but the constructor
        may be called from base classes.

        :param resource_location: URL or other location of the requested resource.
        :param scope: A space-delimited list of scopes to limit access to resource.
        """
        self.resource_location = resource_location
        self.scope = scope

    @abstractmethod
    def get_credential_object(self) -> object:
        """
        Returns a cloud-specific credential object
        """
        pass

    @abstractmethod
    def get_access_token(self) -> str:
        """
        Returns an access token for the respective scope
        """
        pass
