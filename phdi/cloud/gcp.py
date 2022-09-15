from typing import List
from .core import BaseCredentialManager, BaseCloudStorageConnection
import google.auth
import google.auth.transport.requests
from google.auth.credentials import Credentials
from google.cloud import storage


class GcpCredentialManager(BaseCredentialManager):
    """
    This class provides a GCP-specific credential manager.
    """

    @property
    def scope(self) -> str:
        return self.__scope

    @property
    def scoped_credentials(self) -> Credentials:
        return self.__scoped_credentials

    @property
    def project_id(self) -> str:
        return self.__project_id

    def __init__(self, scope: list = None):
        """
        Create a new GcpCredentialManager object.

        :param scope: A list of scopes to limit access to resource.
        """
        self.__scope = scope
        self.__scoped_credentials = None
        self.__project_id = None

        if self.scope is None:
            self.__scope = ["https://www.googleapis.com/auth/cloud-platform"]

    def get_credential_object(self) -> Credentials:
        """
        Get a GCP-specific credential object.

        :return: A scoped instance of the Credentials class from google.auth
            package, refreshed if necessary.
        """
        # Get credentials if they don't exist or are expired.
        if self.__scoped_credentials is None:
            self.__scoped_credentials, self.__project_id = google.auth.default(
                scopes=self.scope
            )
        elif self.__scoped_credentials.expired:
            self.__scoped_credentials, self.__project_id = google.auth.default(
                scopes=self.scope
            )

        return self.__scoped_credentials

    def get_project_id(self) -> str:
        """
        Get the ID of the current GCP project.

        :return: The current GCP project ID.
        """

        if self.__project_id is None:
            self.__scoped_credentials, self.__project_id = google.auth.default(
                scopes=self.scope
            )
        return self.__project_id

    def get_access_token(self) -> str:
        """
        Obtain an access token from GCP.

        :return: The access token, refreshed if necessary.
        """

        creds = self.get_credential_object()
        if not creds.valid:
            request = google.auth.transport.requests.Request()
            creds.refresh(request=request)

        access_token = creds.token

        return access_token


class GcpCloudStorageConnection(BaseCloudStorageConnection):
    """
    This class implements the PHDI cloud storage interface for connecting to Azure.
    """

    @property
    def storage_account_url(self) -> str:
        return self.__storage_account_url

    @property
    def cred_manager(self) -> GcpCredentialManager:
        return self.__cred_manager

    def _get_storage_client(self) -> storage.Client:
        """
        Obtain a client connected to an Azure storage container by
        utilizing the first valid credentials Azure can find. For
        more information on the order in which the credentials are
        checked, see the Azure documentation:
        https://docs.microsoft.com/en-us/azure/developer/python/sdk/authentication-overview#sequence-of-authentication-methods-when-using-defaultazurecredential

        :param container_url: The url at which to access the container
        :return: Azure ContainerClient
        """

        return storage.Client()

    def download_object(
        self, bucket_name: str, filename: str, encoding: str = "UTF-8"
    ) -> str:
        """
        Download a character blob from storage and return it as a string.

        :param container_name: The name of the container containing object to download
        :param filename: Location of file within Azure blob storage
        :param encoding: Encoding applied to the downloaded content
        :return: Character blob (as a string) from given container and filename
        """
        storage_client = self._get_storage_client()
        blob = storage_client.bucket(bucket_name).blob
        return blob.download_as_string(filename)

    def upload_object(
        self,
        message: str,
        bucket_name: str,
        filename: str,
        content_type="application/json",
    ) -> None:
        """
        Upload the content of a given message to Azure blob storage.
        Message can be passed either as a raw string or as JSON.

        :param message: The contents of a message, encoded either as a
          string or in a JSON format
        :param container_name: The name of the target container for upload
        :param filename: Location of file within Azure blob storage
        """

        storage_client = self._get_storage_client()
        bucket = storage_client.bucket(bucket_name)
        destination_blob_name = filename

        blob = bucket.blob(destination_blob_name)
        blob.upload_from_string(data=message, content_type=content_type)

    def list_objects(self, bucket_name: str, prefix: str = "") -> List[str]:
        """
        List names for objects within a container.

        :param container_name: The name of the container to look for objects
        :param prefix: Filter for objects whose filenames begin with this value
        :return: List of names for objects in given container
        """
        storage_client = self._get_storage_client()

        blob_properties_generator = storage_client.list_blobs(
            bucket_name, name_starts_with=prefix
        )

        blob_name_list = []
        for blob_propreties in blob_properties_generator:
            blob_name_list.append(blob_propreties.name)

        return blob_name_list
