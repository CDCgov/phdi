import io
import json
import logging
import requests

from .core import BaseCredentialManager, CloudContainerConnection
from azure.core.credentials import AccessToken
from azure.core.exceptions import ResourceExistsError
from azure.identity import DefaultAzureCredential
from azure.storage.blob import ContainerClient, BlobServiceClient
from datetime import datetime, timezone
from typing import IO, List


class AzureCredentialManager(BaseCredentialManager):
    """
    This class implements the PHDI cloud storage interface for connecting to Azure.
    """

    @property
    def storage_account_url(self) -> str:
        return self.__storage_account_url

    @property
    def scope(self) -> str:
        return self.__scope

    @property
    def access_token(self) -> AccessToken:
        return self.__access_token

    def __init__(self, storage_account_url: str, scope: str = None):
        """
        Create a new AzureCredentialManager object.

        :param storage_account_url: URL or other location of the requested resource.
        :param scope: A space-delimited list of scopes to limit access to resource.
        """
        self.__storage_account_url = storage_account_url
        self.__scope = scope
        self.__access_token = None

        if self.scope is None:
            self.__scope = f"{self.storage_account_url}/.default"

    def get_credential_object(self) -> object:
        """
        Get an Azure-specific credential object.

        :return: Returns an instance of one of the *Credential objects from the
        `azure.identity` package.
        """
        return DefaultAzureCredential()

    def get_access_token(self, force_refresh: bool = False) -> str:
        """
        Obtain an access token from the Azure identity provider.

        :param force_refresh: force token refresh even if the current token is
          still valid
        :return: The access token, refreshed if necessary
        """

        if force_refresh or (self.access_token is None) or self._need_new_token():
            creds = self.get_credential_object()
            self.__access_token = creds.get_token(self.scope)

        return self.access_token.token

    def _need_new_token(self) -> bool:
        """
        Determine whether the token already stored for this object can be reused,
        or if it needs to be re-requested.

        :return: Whether we need a new token (True means we do)
        """
        try:
            current_time_utc = datetime.now(timezone.utc).timestamp()
            return self.access_token.expires_on < current_time_utc
        except AttributeError:
            # access_token not set
            return True


class AzureCloudContainerConnection(CloudContainerConnection):
    """
    This class implements the PHDI cloud storage interface for connecting to Azure.
    """

    @property
    def storage_account_url(self) -> str:
        return self.__storage_account_url

    @property
    def cred_manager(self) -> AzureCredentialManager:
        return self.__cred_manager

    def __init__(self, storage_account_url: str, cred_manager: AzureCredentialManager):
        """
        Create a new AzureCloudContainerConnection object.


        :param storage_account_url: Storage account location of the requested resource.
        :param cred_manager: The Azure credential manager.
        """
        self.__storage_account_url = storage_account_url
        self.__cred_manager = cred_manager

    def _get_container_client(self, container_url: str) -> ContainerClient:
        """
        Obtains a client connected to an Azure storage container by
        utilizing the first valid credentials Azure can find. For
        more information on the order in which the credentials are
        checked, see the Azure documentation:
        https://docs.microsoft.com/en-us/azure/developer/python/sdk/authentication-overview#sequence-of-authentication-methods-when-using-defaultazurecredential

        :param container_url: The url at which to access the container
        :return: An Azure container client for the given container
        """
        creds = self.cred_manager.get_credential_object()
        return ContainerClient.from_container_url(container_url, credential=creds)

    def download_object(
        self, container_name: str, filename: str, stream: IO = None
    ) -> IO:
        """
        Downloads a blob from storage.

        :param container_name: Azure blob container name.
        :param filename: Location of file within Azure blob storage.
        :param stream: (optional) stream object that should be used to write output
          contents of blob.
        :return: The `stream` parameter, if supplied. Otherwise a new
          io.IOBytes object.
        """
        container_location = f"{self.storage_account_url}/{container_name}"
        container_client = self._get_container_client(container_location)
        blob_client = container_client.get_blob_client(filename)

        downloader = blob_client.download_blob()

        if stream is None:
            stream = io.BytesIO()

        downloader.download_to_stream(stream)

        return stream

    def upload_object(
        self,
        container_name: str,
        filename: str,
        message_json: dict = None,
        message: str = None,
    ) -> None:
        """
        Uploads content to Azure blob storage.
        Exactly one of message_json or message should be provided.

        :param container_name: Azure blob container name.
        :param filename: Location of file within Azure blob storage.
        :param message_json: The content of a message a json-formatted dict.
        :param message: The content of a message encoded as a string.
        """
        container_location = f"{self.storage_account_url}/{container_name}"
        container_client = self._get_container_client(container_location)
        blob_client = container_client.get_blob_client(filename)

        if message_json is not None:
            blob_client.upload_blob(
                json.dumps(message_json).encode("utf-8"), overwrite=True
            )
        elif message is not None:
            blob_client.upload_blob(bytes(message, "utf-8"), overwrite=True)

    def list_containers(self) -> List[str]:
        """
        List of names for this CloudContainerConnection's containers

        :return: A list of container names
        """
        creds = self.cred_manager.get_credential_object()
        service_client = BlobServiceClient.from_connection_string(
            self.storage_account_url, credential=creds
        )

        container_properties_generator = service_client.list_containers()

        container_name_list = []
        for container_propreties in container_properties_generator:
            container_name_list.append(container_propreties.name)

        return container_name_list

    def list_objects(self, container_name: str, prefix: str = "") -> List[str]:
        """
        List names for objects within a container

        :param container_name: Azure blob container name.
        :param prefix: Only return objects whose filenames begin with this value
        :return: A list of object names
        """
        container_location = f"{self.storage_account_url}/{container_name}"
        container_client = self._get_container_client(container_location)

        blob_properties_generator = container_client.list_blobs(name_starts_with=prefix)

        blob_name_list = []
        for blob_propreties in blob_properties_generator:
            blob_name_list.append(blob_propreties.name)

        return blob_name_list


def store_message_and_response(
    client: AzureCloudContainerConnection,
    container_name: str,
    message_filename: str,
    response_filename: str,
    message: str,
    response: requests.Response,
) -> None:
    """
    Store information about an incoming message as well as an http response for a
    transaction related to that message.  This method can be used to
    record a failed response to a transaction related to an inbound transaction for
    troubleshooting purposes.

    :param client: An instance of `AzureCloudContainerConnection` used to
      upload the request
    :param container_name: Azure blob container name.
    :param message_filename: The file name to use to store the message in blob storage
    :param response_filename: The file name to use to store the response content
      in blob storage
    :param message: The content of a message encoded as a string.
    :param response: HTTP response information from a transaction related to the
      `message`.
    """
    try:
        # First attempt is storing the message directly in the
        # invalid messages container
        client.upload_object(
            container_name=container_name,
            filename=message_filename,
            message=message,
        )
    except ResourceExistsError:
        logging.warning(f"Attempted to store preexisting resource: {message_filename}")
    try:
        # Then, try to store the response information
        client.upload_object(
            container_name=container_name,
            filename=response_filename,
            message=response.text,
        )
    except ResourceExistsError:
        logging.warning(f"Attempted to store preexisting resource: {response_filename}")
