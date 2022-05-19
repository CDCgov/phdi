import io
import json
import logging
import polling
import requests

from datetime import datetime, timezone
from requests.adapters import HTTPAdapter
from typing import Union, Iterator, Tuple, TextIO
from urllib3 import Retry

from azure.core.credentials import AccessToken
from azure.identity import DefaultAzureCredential
from azure.storage.blob import download_blob_from_url


def generate_filename(blob_name: str, message_index: int) -> str:
    """Strip the file type suffix from the blob name, and append message index."""
    fname = blob_name.split("/")[-1]
    fname, _ = fname.rsplit(".", 1)
    return f"{fname}-{message_index}"


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


def upload_bundle_to_fhir_server(bundle: dict, access_token: str, fhir_url: str):
    """Import a FHIR resource to the FHIR server.
    The submissions may be Bundles or individual FHIR resources.

    :param dict bundle: FHIR bundle (type "batch") to post
    :param str access_token: FHIR Server access token.
    :param str method: HTTP method to use (currently PUT or POST supported)
    """
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "PUT", "POST", "OPTIONS"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    try:
        requests.post(
            fhir_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/fhir+json",
                "Content-Type": "application/fhir+json",
            },
            data=json.dumps(bundle),
        )
    except Exception:
        logging.exception("Request to post Bundle failed for json: " + str(bundle))
        return


def export_from_fhir_server(
    access_token: str,
    fhir_url: str,
    export_scope: str = "",
    since: str = "",
    resource_type: str = "",
    poll_step: float = 30,
    poll_timeout: float = 300,
) -> dict:
    """Initiate a FHIR $export operation, and poll until it completes.
    If the export operation is in progress at the end of poll_timeout,
    :param access_token: Access token string used to connect to FHIR server
    :param fhir_url: FHIR Server base URL
    :param export_scope: Either `Patient` or `Group/[id]` as specified in the FHIR spec
    (https://hl7.org/fhir/uv/bulkdata/export/index.html#bulk-data-kick-off-request)
    :param since: A FHIR instant (https://build.fhir.org/datatypes.html#instant)
    instructing the export to include only resources created or modified after the
    specified instant.
    :param resource_type: A comma-delimited list of resource types to include.  All
    :param poll_step: the number of seconds to wait between poll requests, waiting
    for export files to be generated.
    :param poll_timeout: the maximum number of seconds to wait for export files to
    be generated.
    """
    logging.debug("Initiating export from FHIR server.")
    export_url = _compose_export_url(
        fhir_url=fhir_url,
        export_scope=export_scope,
        since=since,
        resource_type=resource_type,
    )
    logging.debug(f"Composed export URL: {export_url}")
    response = requests.get(
        export_url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/fhir+json",
            "Prefer": "respond-async",
        },
    )
    logging.info(f"Export request completed with status {response.status_code}")

    if response.status_code == 202:

        poll_response = export_from_fhir_server_poll(
            poll_url=response.headers.get("Content-Location"),
            access_token=access_token,
            poll_step=poll_step,
            poll_timeout=poll_timeout,
        )

        if poll_response.status_code == 200:
            logging.debug(f"Export content: {poll_response.text}")
            return poll_response.json()
        else:
            logging.exception("Unexpected response code during export download.")
            raise requests.HTTPError(response=response)


def _compose_export_url(
    fhir_url: str, export_scope: str = "", since: str = "", resource_type: str = ""
) -> str:
    """Generate a query string for the export request.  Details in the FHIR spec:
    https://hl7.org/fhir/uv/bulkdata/export/index.html#query-parameters"""
    export_url = fhir_url
    if export_scope == "Patient" or export_scope.startswith("Group/"):
        export_url += f"/{export_scope}/$export"
    elif export_scope == "":
        export_url += "/$export"
    else:
        raise ValueError("Invalid scope {scope}.  Expected 'Patient' or 'Group/[ID]'.")

    # Start with ? url argument separator, and change it to & after the first parameter
    # is appended to the URL
    separator = "?"
    if since:
        export_url += f"{separator}_since={since}"
        separator = "&"

    if resource_type:
        export_url += f"{separator}_type={resource_type}"
        separator = "&"

    return export_url


def __export_from_fhir_server_poll_call(
    poll_url: str, access_token: str
) -> Union[requests.Response, None]:
    """Poll to see if the export files are ready.  If export is still in progress,
    and we should return null so polling continues.  If the response is 200, then
    the export files are ready, and we return the HTTP response.  Any other status
    either indicates an error or unexpected condition.  In this case raise an error.
    """
    response = requests.get(
        poll_url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/fhir+ndjson",
        },
    )
    if response.status_code == 202:
        # In progress - return None to keep polling
        return
    elif response.status_code == 200:
        # Complete
        return response
    else:
        raise requests.HTTPError(response=response)


def export_from_fhir_server_poll(
    poll_url: str, access_token: str, poll_step: float = 30, poll_timeout: float = 300
) -> requests.Response:
    """Poll for export file avialability after an export has been initiated.

    :param poll_url: URL to poll for export information
    :param access_token: Bearer token used for authentication
    :param poll_step: the number of seconds to wait between poll requests, waiting
    for export files to be generated. defaults to 30
    :param poll_timeout: the maximum number of seconds to wait for export files to
    be generated. defaults to 300
    :raises polling.TimeoutException: If the FHIR server continually returns a 202
    status indicating in progress until the timeout is reached.
    :raises requests.HTTPError: If an unexpected status code is returned.
    :return: The export response obtained from the FHIR server (200 status code)
    """
    response = polling.poll(
        target=__export_from_fhir_server_poll_call,
        args=[poll_url, access_token],
        step=poll_step,
        timeout=poll_timeout,
    )

    # Handle error conditions
    if response.status_code != 200:
        raise requests.HTTPError(
            f"Encountered status {response.status_code} when requesting status"
            + "of export `{poll_url}`"
        )

    # If no error conditions, return response
    return response


def download_from_export_response(
    export_response: dict,
) -> Iterator[Tuple[str, TextIO]]:
    """Accepts the export response content as specified here:
    https://hl7.org/fhir/uv/bulkdata/export/index.html#response---complete-status

    Loops through the "output" array and yields the resource_type (e.g. Patient)
    along with TextIO wrapping ndjson content.

    :param export_response: export response JSON
    :yield: tuple containing resource type (e.g. Patient) AND THE TextIO of the
    downloaded ndjson content for that resource type
    """
    # TODO: Handle error array that could be contained in the response content.

    for export_entry in export_response.get("output", []):
        resource_type = export_entry.get("type")
        blob_url = export_entry.get("url")
        yield (resource_type, _download_export_blob(blob_url=blob_url))


def _download_export_blob(blob_url: str, encoding: str = "utf-8") -> TextIO:
    """Download an export file blob.

    :param blob_url: Blob URL location to download from Azure Blob storage
    :param encoding: encoding to apply to the ndjson content, defaults to "utf-8"
    :return: Downloaded content wrapped in TextIO
    """
    bytes_buffer = io.BytesIO()
    cred = DefaultAzureCredential()
    download_blob_from_url(blob_url=blob_url, output=bytes_buffer, credential=cred)
    text_buffer = io.TextIOWrapper(buffer=bytes_buffer, encoding=encoding, newline="\n")
    text_buffer.seek(0)
    return text_buffer
