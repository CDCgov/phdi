import logging
from typing import List, Literal
import requests

from phdi.cloud.core import BaseCredentialManager
from phdi.transport import http_request_with_retry


def http_request_with_reauth(
    cred_manager: BaseCredentialManager,
    url: str,
    retry_count: int,
    request_type: Literal["GET", "POST"],
    allowed_methods: List[str],
    headers: dict,
    data: dict = None,
) -> requests.Response:
    """
    First, calls :func:`phdi.transport.http.http_request_with_retry`. If the first call
    fails with an authorization error (HTTP status 401), obtains a new token using the
    `cred_manager`. If the original request had an Authorization header, replaces
    it with the new token and re-initiates
    :func:`phdi.transport.http.http_request_with_retry`.

    :param cred_manager: The credential manager used to authenticate to the FHIR server.
    :param url: The url at which to make the HTTP request.
    :param retry_count: The number of times to retry the request, if the
      first attempt fails.
    :param request_type: The type of request to be made.
    :param allowed_methods: The list of allowed HTTP request methods (i.e.,
      POST, PUT, etc.) for the specific URL and query.
    :param headers: JSON-type dictionary of headers to make the request with,
      including Authorization and content-type.
    :param data: JSON data in the case that the request requires data to be
      posted. Default: `None`
    :return: A `requests.Request` object containing the response from the FHIR server.
    """

    response = http_request_with_retry(
        url=url,
        retry_count=retry_count,
        request_type=request_type,
        allowed_methods=allowed_methods,
        headers=headers,
        data=data,
    )

    # Retry with new token in case it expired since creation (or from cache)
    if response.status_code == 401:
        if headers.get("Authorization", "").startswith("Bearer "):
            new_access_token = cred_manager.get_access_token()
            headers["Authorization"] = f"Bearer {new_access_token}"

        response = http_request_with_retry(
            url=url,
            retry_count=retry_count,
            request_type=request_type,
            allowed_methods=allowed_methods,
            headers=headers,
            data=data,
        )

    return response


def upload_bundle_to_fhir_server(
    bundle: dict, cred_manager: BaseCredentialManager, fhir_url: str
) -> requests.Response:
    """
    Uploads a FHIR resource bundle to the FHIR server.

    :param bundle: A FHIR bundle (type "batch" or "transaction") to post.  Each entry in
      the bundle must contain a `request` element in addition to a `resource`.
      The FHIR API provides additional details on creating
      [FHIR-conformant batch/transaction](https://hl7.org/fhir/http.html#transaction)
      bundles.
    :param cred_manager: The credential manager used to authenticate to the FHIR server.
    :param fhir_url: The url of the FHIR server to upload to.
    :return: A `requests.Request` object containing the response from the FHIR server.
    """

    access_token = cred_manager.get_access_token()

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


def fhir_server_get(url: str, cred_manager: BaseCredentialManager) -> requests.Response:
    """
    Submits a GET request to a FHIR server given a url and access token for
    authentication.

    :param url: A URL specifying a GET request on a FHIR server.
    :param cred_manager: The credential manager used to authenticate to the FHIR server.
    :return: A `requests.Request` object containing the response from the FHIR server.
    """
    access_token = cred_manager.get_access_token()
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
    """
    Logs the error for a given an HTTP status code from a FHIR server's response.

    :param status_code: The status code returned by a FHIR server.
    """
    # TODO: We may dedcide to remove logging, and instead report errors back to
    # calling function as raised exceptions.
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
