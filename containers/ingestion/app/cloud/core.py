from abc import ABC
from abc import abstractmethod
from typing import List
from typing import Union


class BaseCredentialManager(ABC):
    """
    Provides a common interface for managing service credentials.
    """

    @abstractmethod
    def get_credential_object(self) -> object:
        """
        Gets a cloud-specific credential object.

        :return: A credential object.
        """
        pass  # pragma: no cover

    @abstractmethod
    def get_access_token(self) -> str:
        """
        Gets an access token using the managed credentials.

        :return: An access token.
        """
        pass  # pragma: no cover


class BaseCloudStorageConnection(ABC):
    @abstractmethod
    def download_object(
        self, container_name: str, filename: str, encoding: str = "utf-8"
    ) -> str:
        """
        Downloads a blob from storage.

        :param container_name: The name of the container containing object to download.
        :param filename: The location of file within storage.
        :param encoding: The character encoding applied to the downloaded content.
        :return: The `stream` parameter, if supplied. Otherwise a new stream object
          containing blob content.
        """
        pass  # pragma: no cover

    @abstractmethod
    def upload_object(
        self,
        message: Union[str, dict],
        container_name: str,
        filename: str,
    ) -> None:
        """
        Uploads the content of a given message to blob storage.
        The message can be passed either as a raw string or as JSON.

        :param message: The contents of a message, encoded either as a
          string or in a JSON format.
        :param container_name: The name of the target container for upload.
        :param filename: The location of file within storage container.
        """
        pass  # pragma: no cover

    @abstractmethod
    def list_containers(self) -> List[str]:
        """
        Lists names for this CloudContainerConnection's containers.

        :return: A list of container names.
        """
        pass  # pragma: no cover

    @abstractmethod
    def list_objects(self, container_name: str, prefix: str) -> List[str]:
        """
        Lists names for objects within a container.

        :param container_name: The name of the container to look for objects.
        :param prefix: Filter the objects returned to filenames beginning
          with this value.
        :return: A list of objects within a container.
        """
        pass  # pragma: no cover
