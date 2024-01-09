import json
from typing import List
from typing import Union

import google.auth.transport.requests
from google.auth.credentials import Credentials
from google.cloud import storage

from .core import BaseCloudStorageConnection
from .core import BaseCredentialManager


class GcpCredentialManager(BaseCredentialManager):
    """
    Provides a GCP-specific credential manager.
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
        Creates a new GcpCredentialManager object.

        :param scope: A list of scopes to limit access to resource.
        """
        self.__scope = scope
        self.__scoped_credentials = None
        self.__project_id = None

        if self.scope is None:
            self.__scope = ["https://www.googleapis.com/auth/cloud-platform"]

    def get_credential_object(self) -> Credentials:
        """
        Gets a GCP-specific credential object.

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
        Gets the ID of the current GCP project.

        :return: The current GCP project ID.
        """

        if self.__project_id is None:
            self.__scoped_credentials, self.__project_id = google.auth.default(
                scopes=self.scope
            )
        return self.__project_id

    def get_access_token(self) -> str:
        """
        Obtains an access token from GCP.

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
    Defines a connection used for interacting with cloud storage in GCP.
    """

    @property
    def storage_client(self) -> storage.Client:
        return self.__storage_client

    def __init__(self):
        """
        Creates a new GcpCloudContainerConnection object.
        """

        self.__storage_client = None

    def _get_storage_client(self) -> storage.Client:
        """
        Obtains a client connected to an GCP storage container by
        utilizing the first valid credentials GCP can find. Credential validation
        is handeled by GCP.

        :return: The GCP storage client.
        """

        if self.__storage_client is None:
            self.__storage_client = storage.Client()

        return self.__storage_client

    def download_object(
        self, container_name: str, filename: str, encoding: str = "utf-8"
    ) -> str:
        """
        Downloads a character blob from storage and returns it as a string.

        :param container_name: The name of the bucket containing object to download.
        :param filename: The location of file within GCP blob storage.
        :param encoding: The encoding applied to the downloaded content.
        :return: A character blob (as a string) from given bucket and filename.
        """
        storage_client = self._get_storage_client()
        blob = storage_client.bucket(container_name).blob(filename)
        return blob.download_as_text(encoding=encoding)

    def upload_object(
        self,
        message: Union[str, dict],
        container_name: str,
        filename: str,
        content_type="application/json",
    ) -> None:
        """
        Uploads the content of a given message to GCP blob storage.
        The message can be passed either as a raw string or as JSON.

        :param message: The contents of a message, encoded either as a
          string or in a JSON-formatted dictionary.
        :param container_name: The name of the target bucket for upload.
        :param filename: The location of file within GCP blob storage.
        """

        storage_client = self._get_storage_client()
        bucket = storage_client.bucket(container_name)

        blob = bucket.blob(filename)

        if isinstance(message, dict):
            message = json.dumps(message).encode("utf-8")

        blob.upload_from_string(data=message, content_type=content_type)

    def list_containers(self) -> List[str]:
        """
        Lists bucket names in storage.

        :return: A list of bucket names in storage.
        """
        storage_client = self._get_storage_client()

        bucket_name_list = []
        for bucket in storage_client.list_buckets():
            bucket_name_list.append(bucket)
        return bucket_name_list

    def list_objects(self, container_name: str, prefix: str = "") -> List[str]:
        """
        Lists names for objects within a bucket.

        :param container_name: The name of the bucket to look for objects.
        :param prefix: Filter the objects returned to filenames beginning
          with this value.
        :return: A list of names for objects in given bucket.
        """
        storage_client = self._get_storage_client()

        blob_properties_generator = storage_client.list_blobs(
            container_name, prefix=prefix
        )

        blob_name_list = []
        for blob_propreties in blob_properties_generator:
            blob_name_list.append(blob_propreties.name)

        return blob_name_list
