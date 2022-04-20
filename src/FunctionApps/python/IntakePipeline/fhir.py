from datetime import datetime, timezone
import json
import logging
import pathlib
import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from azure.core.credentials import AccessToken
from azure.identity import DefaultAzureCredential
from azure.storage.blob import ContainerClient


def get_blob_client(container_url: str) -> ContainerClient:
    """Use whatever creds Azure can find to authenticate with the storage container"""
    creds = DefaultAzureCredential()
    return ContainerClient.from_container_url(container_url, credential=creds)


def generate_filename(blob_name: str, message_index: int) -> str:
    fname = blob_name.split("/")[-1]
    fname, _ = fname.rsplit(".", 1)
    return f"{fname}-{message_index}"


def store_data(
    container_url: str,
    prefix: str,
    filename: str,
    bundle_type: str,
    bundle: dict = None,
    message: str = None,
) -> None:
    """
    Store the given data, which is either a FHIR bundle or an HL7 message in the
    appropriate output container
    """
    client = get_blob_client(container_url)
    blob = client.get_blob_client(str(pathlib.Path(prefix) / bundle_type / filename))
    if bundle is not None:
        blob.upload_blob(json.dumps(bundle).encode("utf-8"))
    elif message is not None:
        blob.upload_blob(bytes(message, "utf-8"))


class AzureFhirserverCredentialManager:
    """Manager for handling Azure credentials for access to the FHIR server"""

    def __init__(self, fhir_url):
        """Credential manager constructor"""
        self.access_token = None
        self.fhir_url = fhir_url

    def get_fhir_url(self):
        """Get FHIR URL"""
        return self.fhir_url

    def get_access_token(self, token_reuse_tolerance: float = 10.0) -> AccessToken:
        """If the token is already set for this object and is not about to expire
        (within token_reuse_tolerance parameter), then return the existing token.
        Otherwise, request a new one.
        :param str token_reuse_tolerance: Number of seconds before expiration
        it is OK to reuse the currently assigned token"""
        if not self._need_new_token(token_reuse_tolerance):
            return self.access_token

        creds = self._get_azure_credentials()
        scope = f"{self.fhir_url}/.default"
        self.access_token = creds.get_token(scope)

        return self.access_token

    def _get_azure_credentials(self):
        """Get default Azure Credentials from login context and related
        Azure configuration."""
        return DefaultAzureCredential()

    def _need_new_token(self, token_reuse_tolerance: float = 10.0) -> bool:
        """Determine whether the token already stored for this object can be reused, or if it
        needs to be re-requested.
        :param str token_reuse_tolerance: Number of seconds before expiration
        it is OK to reuse the currently assigned token"""
        try:
            current_time_utc = datetime.now(timezone.utc).timestamp()
            return (
                self.access_token.expires_on - token_reuse_tolerance
            ) < current_time_utc
        except AttributeError:
            # access_token not set
            return True


def get_fhirserver_cred_manager(fhir_url: str):
    """Get an instance of the Azure FHIR Server credential manager."""
    return AzureFhirserverCredentialManager(fhir_url)


def upload_bundle_to_fhir_server(
    fhirserver_cred_manager: AzureFhirserverCredentialManager, fhir_json: dict
):
    """Import a FHIR resource to the FHIR server.
    The submissions may be Bundles or individual FHIR resources.

    :param AzureFhirserverCredentialManager fhirserver_cred_manager: Credential manager.
    :param dict fhir_json: FHIR resource in json format.
    :param str method: HTTP method to use (currently PUT or POST supported)
    """
    try:
        token = fhirserver_cred_manager.get_access_token()
    except Exception:
        logging.exception("Failed to get access token")
        raise requests.exceptions.HTTPError(
            "Authorization error occurred while processing information into \
            FHIR server."
        )
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "PUT", "POST", "OPTIONS"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    fhir_url = fhirserver_cred_manager.fhir_url
    try:
        requests.post(
            fhir_url,
            headers={
                "Authorization": f"Bearer {token.token}",
                "Accept": "application/fhir+json",
                "Content-Type": "application/fhir+json",
            },
            data=json.dumps(fhir_json),
        )
    except Exception:
        logging.exception("Request to post Bundle failed for json: " + str(fhir_json))
        return
