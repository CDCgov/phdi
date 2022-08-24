import json

from .core import BaseCredentialManager, BaseCloudContainerConnection
from azure.core.credentials import AccessToken
from azure.identity import DefaultAzureCredential
from azure.storage.blob import ContainerClient, BlobServiceClient
from datetime import datetime, timezone
from typing import List


class AzureCredentialManager(BaseCredentialManager):
    """
    This class defines a credential manager for connecting to Azure.
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
        This returns an instance of one of the *Credential objects from the
        `azure.identity` package.
        """
        return DefaultAzureCredential()

    def get_access_token(self, force_refresh: bool = False) -> str:
        """
        Obtain an access token from the Azure identity provider.  Return the
        access token string, refreshed if expired or force_refresh is specified.

        :param force_refresh: force token refresh even if the current token is
          still valid
        """
        if force_refresh or (self.access_token is None) or self._need_new_token():
            creds = self.get_credential_object()
            self.__access_token = creds.get_token(self.scope)

        return self.access_token.token

    def _need_new_token(self) -> bool:
        """
        Determine whether the token already stored for this object can be reused,
        or if it needs to be re-requested.

        """
        try:
            current_time_utc = datetime.now(timezone.utc).timestamp()
            return self.access_token.expires_on < current_time_utc
        except AttributeError:
            # access_token not set
            return True


class AzureCloudContainerConnection(BaseCloudContainerConnection):
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

        :param storage_account_url: Storage account location of the requested resource
        :param cred_manager: The Azure credential manager
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
        """
        creds = self.cred_manager.get_credential_object()
        return ContainerClient.from_container_url(container_url, credential=creds)

    def download_object(
        self, container_name: str, filename: str, encoding: str = "UTF-8"
    ) -> str:
        """
        Downloads a character blob from storage and returns it as a string.

        :param container_name: The name of the container containing object to download
        :param filename: Location of file within Azure blob storage
        :param encoding: Encoding applied to the downloaded content
        """
        container_location = f"{self.storage_account_url}/{container_name}"
        container_client = self._get_container_client(container_location)
        blob_client = container_client.get_blob_client(filename)

        downloader = blob_client.download_blob()

        downloaded_text = downloader.content_as_text(encoding=encoding)

        return downloaded_text

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

        :param container_name: The name of the target container for upload
        :param filename: Location of file within Azure blob storage
        :param message_json: The content of a message in JSON format
        :param message: The content of a message encoded as a string
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
        List names for this CloudContainerConnection's containers.
        """
        creds = self.cred_manager.get_credential_object()
        service_client = BlobServiceClient(
            account_url=self.storage_account_url, credential=creds
        )
        container_properties_generator = service_client.list_containers()

        container_name_list = []
        for container_propreties in container_properties_generator:
            container_name_list.append(container_propreties.name)

        return container_name_list

    def list_objects(self, container_name: str, prefix: str = "") -> List[str]:
        """
        List names for objects within a container.

        :param container_name: The name of the container to look for objects
        :param prefix: Filter for objects whose filenames begin with this value
        """
        container_location = f"{self.storage_account_url}/{container_name}"
        container_client = self._get_container_client(container_location)

        blob_properties_generator = container_client.list_blobs(name_starts_with=prefix)

        blob_name_list = []
        for blob_propreties in blob_properties_generator:
            blob_name_list.append(blob_propreties.name)

        return blob_name_list
