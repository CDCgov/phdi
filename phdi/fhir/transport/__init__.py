import logging
import requests

from phdi.cloud.core import BaseCredentialManager
from phdi.transport import http_request_with_retry


def http_request_with_reauth(
    cred_manager: BaseCredentialManager,
    **kwargs: dict,
) -> requests.Response:
    """
    First, call :func:`utils.http_request_with_retry`.  If the first call failed
    with an authorization error (HTTP status 401), obtain a new token using the
    `cred_manager`, and if the original request had an Authorization header, replace
    with the new token and re-initiate :func:`utils.http_request_with_retry`.

    :param cred_manager: credential manager used to obtain a new token, if necessary
    :param kwargs: keyword arguments passed to :func:`utils.http_request_with_retry`
      this function only supports passing keyword args, not positional args to
      http_request_with_retry
    :return: A requests.Request object containing the response from the FHIR server.
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


def upload_bundle_to_fhir_server(
    bundle: dict, cred_manager: BaseCredentialManager, fhir_url: str
) -> requests.Response:
    """
    Import a FHIR resource to the FHIR server.
    The submissions may be Bundles or individual FHIR resources.

    :param bundle: FHIR bundle (type "batch") to post
    :param access_token: FHIR Server access token
    :param fhir_url: The url of the FHIR server to upload to
    :return: A requests.Request object containing the response from the FHIR server.
    """

    access_token = cred_manager.get_access_token().token

    response = http_request_with_reauth(
        cred_manager=cred_manager,
        url=fhir_url,
        retry_count=3,
        request_type="POST",
        allowed_methods=["POST"],
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/fhir+json",
            "Content-Type": "application/fhir+json",
        },
        data=bundle,
    )

    # FHIR uploads are sent as a batch.  Although the batch succeeds,
    # individual entries within the batch may fail, so we log them here
    if response.status_code == 200:
        response_json = response.json()
        entries = response_json.get("entry", [])
        for entry_index, entry in enumerate(entries):
            entry_response = entry.get("response", {})

            # FHIR bundle.entry.response.status is string type - integer status code
            # plus may inlude a message
            if entry_response and not entry_response.get("status", "").startswith(
                "200"
            ):
                _log_fhir_server_error(
                    status_code=int(entry_response["status"][0:3]),
                    batch_entry_index=entry_index,
                )

    else:
        _log_fhir_server_error(response.status_code)

    return response


def fhir_server_get(
    url: str, cred_manager: BaseCredentialManager
) -> requests.models.Response:
    """
    Submit a GET request to a FHIR server given a url and access token for
    authentication.

    :param url: URL specifying a GET request on a FHIR server.
    :param cred_manager: Service used to get an access token used to make a
        request.
    :return: A requests.Request object containing the response from the FHIR server.
    """
    access_token = cred_manager.get_access_token().token
    # Open connection to the export operation and kickoff process
    response = http_request_with_reauth(
        cred_manager=cred_manager,
        url=url,
        retry_count=3,
        request_type="GET",
        allowed_methods=["GET"],
        headers={"Authorization": f"Bearer {access_token}"},
    )

    _log_fhir_server_error(response.status_code)

    return response


def _log_fhir_server_error(status_code: int, batch_entry_index: int = None) -> None:
    """Given an HTTP status code from a FHIR server's response, log the specified error.

    :param status_code: Status code returned by a FHIR server
    """

    batch_decorator = ""
    if batch_entry_index is not None:
        batch_decorator = (
            f"in zero-based message index {batch_entry_index} of FHIR batch "
        )

    if status_code == 401:
        logging.error(
            f"FHIR SERVER ERROR {batch_decorator}- Status Code 401: Failed to "
            + "authenticate."
        )

    elif status_code == 403:
        logging.error(
            f"FHIR SERVER ERROR {batch_decorator}- Status Code 403: User does not "
            + "have permission to make that request."
        )

    elif status_code == 404:
        logging.error(
            f"FHIR SERVER ERROR {batch_decorator}- Status Code 404: Server or "
            + "requested data not found."
        )

    elif status_code == 410:
        logging.error(
            f"FHIR SERVER ERROR {batch_decorator}- Status Code 410: Server has "
            + "deleted this cached data."
        )

    elif str(status_code).startswith(("4", "5")):
        error_message = (
            f"FHIR SERVER ERROR {batch_decorator}- Status code {status_code}"
        )
        logging.error(error_message)
