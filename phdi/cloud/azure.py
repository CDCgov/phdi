import json
from datetime import datetime
from datetime import timezone
from typing import List
from typing import Literal
from typing import Union

from azure.core.credentials import AccessToken
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.storage.blob import BlobServiceClient
from azure.storage.blob import ContainerClient

from phdi.cloud.core import BaseCloudStorageConnection
from phdi.cloud.core import BaseCredentialManager


class AzureCredentialManager(BaseCredentialManager):
    """
    Defines a credential manager used for connecting to Azure.
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

    def __init__(self, resource_location: str = None, scope: str = None):
        """
        Creates a new AzureCredentialManager object.

        :param resource_location: The URL or other location of the requested resource.
        :param scope: A space-delimited list of scopes to limit access to resource.
          Default: `None`
        """
        self.__resource_location = resource_location
        self.__scope = scope
        self.__access_token = None

        if self.scope is None:
            self.__scope = f"{self.resource_location}/.default"

    def get_credential_object(self) -> object:
        """
        Gets an Azure-specific credential object.

        :return: An instance of one of the \\*Credential objects from the
          `azure.identity` package.
        """
        return DefaultAzureCredential()

    def get_access_token(self, force_refresh: bool = False) -> str:
        """
        Obtains an access token from the Azure identity provider. Returns the
        access token string, refreshed if expired or force_refresh is specified.

        :param force_refresh: `True` if a new token should be requested, regardless
          of expiration timestamp. `False` otherwise. Default: `False`
        :return: An Azure access token.
        """
        if force_refresh or (self.access_token is None) or self._need_new_token():
            creds = self.get_credential_object()
            self.__access_token = creds.get_token(self.scope)

        return self.access_token.token

    def _need_new_token(self) -> bool:
        """
        Determines whether the token already stored for this object can be reused,
        or if it needs to be re-requested. A new token is needed if a token has not
        yet been created, or if the current token has expired.

        :return: True if a new Azure access token is needed; false otherwise.
        """
        try:
            current_time_utc = datetime.now(timezone.utc).timestamp()
            return self.access_token.expires_on < current_time_utc
        except AttributeError:
            # access_token not set
            return True

    def get_secret(self, secret_name: str, key_vault_name: str) -> str:
        """
        Get the value of a secret from an Azure key vault given the names of the vault
        and the secret.

        :param secret_name: The name of the secret whose value should be retrieved from
            the key vault.
        :param key_vault_name: The name of the key vault where the secret is stored.
        :return: The value of the secret specified by secret_name.
        """

        vault_url = f"https://{key_vault_name}.vault.azure.net"
        secret_client = SecretClient(
            vault_url=vault_url, credential=self.get_credential_object()
        )
        return secret_client.get_secret(secret_name).value


class AzureCloudContainerConnection(BaseCloudStorageConnection):
    """
    Defines a connection used for interacting with cloud storage in Azure.
    """

    @property
    def storage_account_url(self) -> str:
        return self.__storage_account_url

    @property
    def cred_manager(self) -> AzureCredentialManager:
        return self.__cred_manager

    def __init__(self, storage_account_url: str, cred_manager: AzureCredentialManager):
        """
        Creates a new AzureCloudContainerConnection object.

        :param storage_account_url: The storage account location of the requested
          resource.
        :param cred_manager: The credential manager used to authenticate to the
          FHIR server.
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

        :param container_url: The url at which to access the container.
        :return: The Azure `ContainerClient`.
        """
        creds = self.cred_manager.get_credential_object()
        return ContainerClient.from_container_url(container_url, credential=creds)

    def download_object(
        self,
        container_name: str,
        filename: str,
        encoding: Literal[None, str] = "UTF-8",
    ) -> Literal[str, bytes]:
        """
        Downloads a blob from storage and returns it as a string or bytes.

        :param container_name: The name of the container containing object to download.
        :param filename: The location of the file within Azure blob storage.
        :param encoding: The encoding applied to the downloaded content. If set to None
            then the blob contents will be returned as bytes. Default: UTF-8
        :return: A character blob as a string from the given container and filename.
        """
        container_location = f"{self.storage_account_url}/{container_name}"
        container_client = self._get_container_client(container_location)
        blob_client = container_client.get_blob_client(filename)

        downloader = blob_client.download_blob(encoding=encoding)

        blob_contents = downloader.readall()

        return blob_contents

    def upload_object(
        self,
        message: Union[str, dict],
        container_name: str,
        filename: str,
    ) -> None:
        """
        Uploads the content of a given message to Azure blob storage.
        The message can be passed either as a raw string or as JSON.

        :param message: The contents of a message, encoded either as a
          string or a JSON-formatted dictionary.
        :param container_name: The name of the target container for upload.
        :param filename: The location of file to upload within Azure blob storage.
        """
        container_location = f"{self.storage_account_url}/{container_name}"
        container_client = self._get_container_client(container_location)
        blob_client = container_client.get_blob_client(filename)

        if isinstance(message, str):
            blob_client.upload_blob(bytes(message, "utf-8"), overwrite=True)
        elif isinstance(message, dict):
            blob_client.upload_blob(json.dumps(message).encode("utf-8"), overwrite=True)

    def list_containers(self) -> List[str]:
        """
        Lists names for this CloudContainerConnection's containers.

        :return: A list of container names.
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
        Lists names for objects within a container.

        :param container_name: The name of the container to look for objects.
        :param prefix: Filter the objects returned to filenames beginning
          with this value.
        :return: A list of names for objects in given container.
        """
        container_location = f"{self.storage_account_url}/{container_name}"
        container_client = self._get_container_client(container_location)

        blob_properties_generator = container_client.list_blobs(name_starts_with=prefix)

        blob_name_list = []
        for blob_propreties in blob_properties_generator:
            blob_name_list.append(blob_propreties.name)

        return blob_name_list

    def blob_exists(self, container_name: str, filename: str) -> bool:
        """
        Check if a blob exists within a container given its name and the name of the
        container.

        :param container_name: The name of the container to look for the blob in.
        :param filename: The name of the blob to check the existence of.
        :param prefix: Filter the objects returned to filenames beginning
          with this value.
        :return: A boolean of true if the file exists and false if it does not.
        """

        container_location = f"{self.storage_account_url}/{container_name}"
        container_client = self._get_container_client(container_location)
        blob_client = container_client.get_blob_client(filename)
        return blob_client.exists()
