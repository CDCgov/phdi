import json
import pathlib
from azure.identity import DefaultAzureCredential
from azure.storage.blob import ContainerClient
from datetime import datetime, timezone
from azure.core.credentials import AccessToken


class AzureFhirServerCredentialManager:
    """
    A class that manages handling Azure credentials for access to the FHIR server.
    """

    def __init__(self, fhir_url: str):
        self.access_token = None
        self.fhir_url = fhir_url

    def get_fhir_url(self) -> str:
        return self.fhir_url

    def get_access_token(self, token_reuse_tolerance: float = 10.0) -> AccessToken:
        """
        Obtain an access token for the FHIR server the manager is pointed at.
        If the token is already set for this object and is not about to expire
        (within token_reuse_tolerance parameter), then return the existing token.
        Otherwise, request a new one.

        :param token_reuse_tolerance: Number of seconds before expiration; it
        is okay to reuse the currently assigned token
        """
        if not self._need_new_token(token_reuse_tolerance):
            return self.access_token

        # Obtain a new token if ours is going to expire soon
        creds = DefaultAzureCredential()
        scope = f"{self.fhir_url}/.default"
        self.access_token = creds.get_token(scope)
        return self.access_token

    def _need_new_token(self, token_reuse_tolerance: float = 10.0) -> bool:
        """
        Determine whether the token already stored for this object can be reused,
        or if it needs to be re-requested.

        :param token_reuse_tolerance: Number of seconds before expiration
        :return: Whether we need a new token (True means we do)
        """
        try:
            current_time_utc = datetime.now(timezone.utc).timestamp()
            return (
                self.access_token.expires_on - token_reuse_tolerance
            ) < current_time_utc
        except AttributeError:
            # access_token not set
            return True


def get_blob_client(container_url: str) -> ContainerClient:
    """
    Obtains a client connected to an Azure storage container by
    utilizing the first valid credentials Azure can find. For
    more information on the order in which the credentials are
    checked, see the Azure documentation:
    https://docs.microsoft.com/en-us/azure/developer/python/sdk/authentication-overview#sequence-of-authentication-methods-when-using-defaultazurecredential

    :param container_url: The url at which to access the container
    :return: An Azure container client for the given container
    """
    creds = DefaultAzureCredential()
    return ContainerClient.from_container_url(container_url, credential=creds)


def store_data(
    container_url: str,
    prefix: str,
    filename: str,
    bundle_type: str,
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
    :param bundle_type: The type of data (FHIR or HL7) being written
    :param message_json: The content of a message encoded in json
      format. Used when the input data type is FHIR.
    :param message: The content of a message encoded as a raw bytestring.
      Used when the input data type is HL7.
    """
    client = get_blob_client(container_url)
    blob = client.get_blob_client(str(pathlib.Path(prefix) / bundle_type / filename))
    if message_json is not None:
        blob.upload_blob(json.dumps(message_json).encode("utf-8"), overwrite=True)
    elif message is not None:
        blob.upload_blob(bytes(message, "utf-8"), overwrite=True)
