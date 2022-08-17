from .core import BaseCredentialManager
import google.auth
import google.auth.transport.requests
from google.auth.credentials import Credentials


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

        :return: Returns a scoped instance of the Credentials class from google.auth
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
