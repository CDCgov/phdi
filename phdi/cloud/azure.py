import io
import json
import logging
import requests

from .core import BaseCredentialManager, CloudContainerConnection
from azure.core.credentials import AccessToken
from azure.core.exceptions import ResourceExistsError
from azure.identity import DefaultAzureCredential
from azure.storage.blob import ContainerClient
from datetime import datetime, timezone
from typing import IO


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

    @property
    def access_token(self) -> AccessToken:
        return self.__access_token

    def __init__(self, resource_location: str, scope: str = None):
        """
        Create a new AzureCredentialManager object.

        :param resource_location: URL or other location of the requested resource.
        :param scope: A space-delimited list of scopes to limit access to resource.
        """
        self.__resource_location = resource_location
        self.__scope = scope
        self.__access_token = None

        if self.scope is None:
            self.__scope = f"{self.resource_location}/.default"

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
    @property
    def resource_location(self) -> str:
        return self.__resource_location

    @property
    def scope(self) -> str:
        return self.__scope

    def __init__(self, resource_location: str, cred_manager: BaseCredentialManager):
        """
        Create a new AzureCloudContainerConnection object.


        :param resource_location: URL or other location of the requested resource.
        :param cred_manager: The Azure credential manager.
        """
        self.__resource_location = resource_location
        self.__cred_manager = cred_manager

    def _get_blob_client(self, container_url: str) -> ContainerClient:
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
        self, container_name: str, filename: str, io_stream: IO = None
    ) -> IO:
        container_location = f"{self.resource_location}/{container_name}"
        container_client = self._get_blob_client(container_location)
        blob_client = container_client.get_blob_client(filename)

        downloader = blob_client.download_blob()

        if io_stream is None:
            io_stream = io.BytesIO()

        downloader.download_to_stream(io_stream)

        return io_stream

    def upload_object(
        self,
        container_name: str,
        filename: str,
        message_json: dict = None,
        message: str = None,
    ) -> None:
        """
        Stores provided data, which is either a FHIR bundle or an HL7 message,
        in an appropriate output container.

        :param container_url: The url at which to access the container
        :param prefix: The "filepath" prefix used to navigate the
        virtual directories to the output container
        :param filename: The name of the file to write the data to
        :param bundle_type: The type of data being written (VXU, ELR, etc)
        :param message_json: The content of a message encoded in json format.
        :param message: The content of a message encoded as a string.
        """
        container_location = f"{self.resource_location}/{container_name}"
        container_client = self._get_blob_client(container_location)
        blob_client = container_client.get_blob_client(filename)

        if message_json is not None:
            blob_client.upload_blob(
                json.dumps(message_json).encode("utf-8"), overwrite=True
            )
        elif message is not None:
            blob_client.upload_blob(bytes(message, "utf-8"), overwrite=True)

    def list_containers(self):
        return super().list_containers()

    def list_objects(self):
        return super().list_objects()


def store_message_and_response(
    client: AzureCloudContainerConnection,
    container_name: str,
    message_filename: str,
    response_filename: str,
    message: str,
    response: requests.Response,
):
    """
    Store information about an incoming message as well as an http response for a
    transaction related to that message.  This method can be used to
    record a failed response to a transaction related to an inbound transaction for
    troubleshooting purposes.

        :param client: An instance of `AzureCloudContainerConnection` used to
          upload the request
        :param container_url: The url at which to access the container
        :param prefix: The "filepath" prefix used to navigate the
          virtual directories to the output container
        :param bundle_type: The type of data being written
        :param message_filename: The file name to use to store the message
          in blob storage
        :param response_filename: The file name to use to store the response content
          in blob storage
        :param message: The content of a message encoded as a string.
        :param response: HTTP response information from a transaction related to the
          `message`.
    """
    try:
        # First attempt is storing the message directly in the
        # invalid messages container
        client.store_data(
            container_name=container_name,
            filename=message_filename,
            message=message,
        )
    except ResourceExistsError:
        logging.warning(f"Attempted to store preexisting resource: {message_filename}")
    try:
        # Then, try to store the response information
        client.store_data(
            container_name=container_name,
            filename=response_filename,
            message=response.text,
        )
    except ResourceExistsError:
        logging.warning(f"Attempted to store preexisting resource: {response_filename}")
