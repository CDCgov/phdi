from abc import ABC, abstractmethod
from typing import Any, Union, IO


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
    def get_access_token(self) -> str:
        """
        Returns an access token using the managed credentials
        """
        pass


class CloudContainerConnection(ABC):
    def __init__(self, resource_location: str, cred_manager: BaseCredentialManager):
        """
        Create a new BaseCredentialManager object.
        This object type is not intended to be called directly, but the constructor
        may be called from base classes.

        :param resource_location: URL or other location of the requested resource.
        :param scope: A space-delimited list of scopes to limit access to resource.
        """
        self.resource_location = resource_location
        self.cred_manager = cred_manager

    @abstractmethod
    def download_object(
        self, container_name: str, filename: str, cred_manager: BaseCredentialManager
    ) -> Any:
        pass

    @abstractmethod
    def upload_object(
        self,
        data: Union[str, dict, IO],
        container_name: str,
        filename: str,
        cred_manager: BaseCredentialManager,
    ) -> None:
        pass

    @abstractmethod
    def list_containers(self):
        pass

    @abstractmethod
    def list_objects(self):
        pass
