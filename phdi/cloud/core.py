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


class CloudContainerConnection(ABC):
    @abstractmethod
    def download_object(
        self, container_name: str, filename: str, stream: IO = None
    ) -> IO:
        """
        Downloads a blob from storage.

        :param container_name: Storage container name.
        :param filename: Location of file within storage.
        :param stream: (optional) stream object that should be used to write output
          contents of blob.
        :return: The `stream` parameter, if supplied. Otherwise a new stream object
          containing blob content.
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

        :param container_name: Storage container name.
        :param filename: Location of file within storage container.
        :param message_json: The content of a message a json-formatted dict.
        :param message: The content of a message encoded as a string.
        """
        pass

    @abstractmethod
    def list_containers(self) -> List[str]:
        """
        List names for this CloudContainerConnection's containers

        :return: A list of container names
        """
        pass

    @abstractmethod
    def list_objects(self) -> List[str]:
        """
        List names for objects within a container

        :param container_name: Storage container name.
        :param prefix: Only return objects whose filenames begin with this value
        :return: A list of object names
        """
        pass
