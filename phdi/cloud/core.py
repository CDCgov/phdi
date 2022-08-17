from abc import ABC, abstractmethod
from typing import IO, List


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


class BaseCloudContainerConnection(ABC):
    @abstractmethod
    def download_object(
        self, container_name: str, filename: str, stream: IO = None
    ) -> IO:
        """
        Downloads a blob from storage.  Returns the `stream` parameter, if supplied.
        Otherwise a new stream object containing blob content.

        :param container_name: The name of the container containing object to download
        :param filename: Location of file within storage.
        :param stream: (optional) stream object that should be used to write output
          contents of blob.
        """
        pass

    @abstractmethod
    def upload_object(
        self,
        container_name: str,
        filename: str,
        message_json: dict = None,
        message: str = None,
    ) -> None:
        """
        Uploads content to storage.
        Exactly one of message_json or message should be provided.

        :param container_name: The name of the target container for upload
        :param filename: Location of file within storage container.
        :param message_json: The content of a message in JSON format.
        :param message: The content of a message encoded as a string.
        """
        pass

    @abstractmethod
    def list_containers(self) -> List[str]:
        """
        List names for this CloudContainerConnection's containers

        """
        pass

    @abstractmethod
    def list_objects(self) -> List[str]:
        """
        List names for objects within a container

        :param container_name: The name of the container to look for objects
        :param prefix: Only return objects whose filenames begin with this value
        """
        pass
