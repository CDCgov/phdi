import json
import logging
import pathlib

from azure.core.credentials import AccessToken
from azure.core.exceptions import ResourceExistsError
from azure.identity import DefaultAzureCredential
from azure.storage.blob import ContainerClient
from datetime import datetime, timezone
from phdi_building_blocks.utils import http_request_with_retry
from requests import Response


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


def _http_request_with_reauth(
    cred_manager: AzureFhirServerCredentialManager,
    **kwargs: dict,
) -> Response:
    """
    First, call :func:`utils.http_request_with_retry`.  If the first call failed
    with an authorization error (HTTP status 401), obtain a new token using the
    `cred_manager`, and if the original request had an Authorization header, replace
    with the new token and re-initiate :func:`utils.http_request_with_retry`.

    :param cred_manager: credential manager used to obtain a new token, if necessary
    :param kwargs: keyword arguments passed to :func:`utils.http_request_with_retry`
    this function only supports passing keyword args, not positional args to
    http_request_with_retry
    """

    response = http_request_with_retry(**kwargs)

    # Retry with new token in case it expired since creation (or from cache)
    if response.status_code == 401:
        headers = kwargs.get("headers")
        if headers.get("Authorization", "").startswith("Bearer "):
            new_access_token = cred_manager.get_access_token().token
            headers["Authorization"] = f"Bearer {new_access_token}"

        response = http_request_with_retry(**kwargs)

    return response


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
    :param bundle_type: The type of data being written (VXU, ELR, etc)
    :param message_json: The content of a message encoded in json format.
    :param message: The content of a message encoded as a string.
    """
    client = get_blob_client(container_url)
    blob = client.get_blob_client(str(pathlib.Path(prefix) / bundle_type / filename))
    if message_json is not None:
        blob.upload_blob(json.dumps(message_json).encode("utf-8"), overwrite=True)
    elif message is not None:
        blob.upload_blob(bytes(message, "utf-8"), overwrite=True)


def store_message_and_response(
    container_url: str,
    prefix: str,
    bundle_type: str,
    message_filename: str,
    response_filename: str,
    message: str,
    response: Response,
):
    """
    Store information about an incoming message as well as an http response for a
    transaction related to that message.  This method can be used to
    record a failed response to a transaction related to an inbound transaction for
    troubleshooting purposes.

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
        store_data(
            container_url=container_url,
            prefix=prefix,
            filename=message_filename,
            bundle_type=bundle_type,
            message=message,
        )
    except ResourceExistsError:
        logging.warning(f"Attempted to store preexisting resource: {message_filename}")
    try:
        # Then, try to store the response information
        store_data(
            container_url=container_url,
            prefix=prefix,
            filename=response_filename,
            bundle_type=bundle_type,
            message=response.text,
        )
    except ResourceExistsError:
        logging.warning(f"Attempted to store preexisting resource: {response_filename}")
