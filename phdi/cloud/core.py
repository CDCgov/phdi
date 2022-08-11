from abc import ABC, abstractmethod


class BaseCredentialManager(ABC):
    """
    This class is intended to provide a common interface for managing service
    credentials.
    """

    @abstractmethod
    def get_credential_object(self) -> object:
        """
        Returns a cloud-specific credential object
        """
        pass

    @abstractmethod
    def get_access_token(self) -> object:
        """
        Returns an access token using the managed credentials
        """
        pass
