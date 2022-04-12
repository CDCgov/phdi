from datetime import datetime, timezone
import io
import json
import logging
import pathlib
import requests
from requests.adapters import HTTPAdapter
import uuid
from urllib3 import Retry

from typing import Iterator, IO

from azure.core.credentials import AccessToken
from azure.identity import DefaultAzureCredential
from azure.storage.blob import ContainerClient


def get_blob_client(container_url: str) -> ContainerClient:
    """Use whatever creds Azure can find to authenticate with the storage container"""
    creds = DefaultAzureCredential().get_token()
    return ContainerClient.from_container_url(container_url, credential=creds)


def get_blobs(container_url: str, container_prefix: str) -> Iterator[IO]:
    """Grabs blob files from the container as a readable file-like iterator"""
    client = get_blob_client(container_url)
    for props in client.list_blobs(name_starts_with=container_prefix):
        logging.info(f"reading blob {props.name}")
        if props.size > 0:
            # If it's an actual file, download it and yield out the individual records
            blob_client = client.get_blob_client(props)
            yield io.BytesIO(blob_client.download_blob().content_as_bytes())
    return


def read_fhir_bundles(container_url: str, container_prefix: str) -> Iterator[dict]:
    """Reads FHIR bundle dicts from Azure blob storage as an iterator"""
    for fp in get_blobs(container_url, container_prefix):
        for line in fp:
            try:
                yield json.loads(line)
            except Exception:
                logging.exception("failed to read json contents in line, skipping file")
                break


def store_bundle(container_url: str, prefix: str, bundle: dict) -> None:
    """Store the given bundle in the output container, in FHIR format"""
    client = get_blob_client(container_url)
    blob = client.get_blob_client(str(pathlib.Path(prefix) / f"{uuid.uuid4()}.fhir"))
    blob.upload_blob(json.dumps(bundle).encode("utf-8"))


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
        self.access_token = creds.get_token(self.fhir_url)

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
    The submissions may Bundles or individual FHIR resources.

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
