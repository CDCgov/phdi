import polling
import requests

from phdi.fhir.transport.http import http_request_with_reauth
from phdi.cloud.core import BaseCredentialManager
from typing import Union


def export_from_fhir_server(
    cred_manager: BaseCredentialManager,
    fhir_url: str,
    export_scope: str = "",
    since: str = "",
    resource_type: str = "",
    container: str = "",
    poll_step: float = 30,
    poll_timeout: float = 300,
) -> dict:
    """
    Initiate a FHIR $export operation, and poll until it completes.
    If the export operation is in progress at the end of poll_timeout,
    use the default polling behavior to do the last function check
    before shutting down the request.

    :param cred_manager: Service used to get an access token used to make a request
    :param fhir_url: FHIR Server base URL
    :param export_scope: Either `Patient` or `Group/[id]` as specified in the FHIR spec
      (https://hl7.org/fhir/uv/bulkdata/export/index.html#bulk-data-kick-off-request)
    :param since: A FHIR instant (https://build.fhir.org/datatypes.html#instant)
      instructing the export to include only resources created or modified after the
      specified instant
    :param resource_type: A comma-delimited list of FHIR resource types to include
    :param container: The name of the Azure blob container used to store exported files
    :param poll_step: The number of seconds to wait between poll requests, waiting
      for export files to be generated
    :param poll_timeout: The maximum number of seconds to wait for export files to
      be generated
    :return: The JSON-formatted HTTP response of a completed export operation as a dict
    """

    # Combine template variables into export endpoint
    access_token = cred_manager.get_access_token()
    export_url = _compose_export_url(
        fhir_url=fhir_url,
        export_scope=export_scope,
        since=since,
        resource_type=resource_type,
        container=container,
    )

    # Open connection to the export operation and kickoff process
    response = http_request_with_reauth(
        cred_manager=cred_manager,
        url=export_url,
        retry_count=3,
        request_type="GET",
        allowed_methods=["GET"],
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/fhir+json",
            "Prefer": "respond-async",
        },
    )

    if response.status_code == 202:

        # Repeatedly poll the endpoint the FHIR server creates for us
        # until either the connection times out (as we configured) or
        # we have the response in hand
        poll_response = export_from_fhir_server_poll(
            poll_url=response.headers.get("Content-Location"),
            cred_manager=cred_manager,
            poll_step=poll_step,
            poll_timeout=poll_timeout,
        )

        # We successfully completed the full export
        if poll_response.status_code == 200:
            return poll_response.json()

        # Didn't complete / encountered unexpected behavior
        else:
            raise requests.HTTPError(response=poll_response)


def export_from_fhir_server_poll(
    poll_url: str,
    cred_manager: BaseCredentialManager,
    poll_step: float = 30,
    poll_timeout: float = 300,
) -> requests.Response:
    """
    Poll an endpoint to retrieve an export file after an export run has been initiated.

    :param poll_url: URL to poll for export information
    :param cred_manager: Service used to get an access token used to make a request
    :param poll_step: the number of seconds to wait between poll requests, waiting
      for export files to be generated
    :param poll_timeout: the maximum number of seconds to wait for export files to
      be generated
    :return: A response from polled endpoint
    :raises polling.TimeoutException: If the FHIR server continually returns a 202
      status indicating in progress until the timeout is reached
    :raises requests.HTTPError: If an unexpected status code is returned
    """
    response = polling.poll(
        target=_export_from_fhir_server_poll_call,
        args=[poll_url, cred_manager],
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


def _compose_export_url(
    fhir_url: str,
    export_scope: str = "",
    since: str = "",
    resource_type: str = "",
    container: str = "",
) -> str:
    """
    Generate a query string for the export request.  Details in the FHIR spec:
    https://hl7.org/fhir/uv/bulkdata/export/index.html#query-parameters

    :param fhir_url: The url of the FHIR server to export from
    :param export_scope: The data we want back (e.g. Patients)
    :param since: We'll get all FHIR resources that have been updated
      since this given timestamp
    :param resource_type: Comma-delimited list of resource types we want
      back
    :param container: The container where we want to store the uploaded
    files
    :return: An export url string
    """
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

    if container:
        export_url += f"{separator}_container={container}"
        separator = "&"

    return export_url


def _export_from_fhir_server_poll_call(
    poll_url: str, cred_manager: BaseCredentialManager
) -> Union[requests.Response, None]:
    """
    Helper method for use with `polling` module to see if the export files are ready
    based on received status code. If export is still in progress, then we should
    return None so polling continues. If the response is 200, then the export files are
    ready, and we return the HTTP response. Any other status either indicates an error
    or unexpected condition. In this case raise an error.

    :param poll_url: The endpoint the FHIR server gave us to query for if
      our files are ready
    :param cred_manager: Service used to get an access token used to make a request
    :return: An HTTP response (if 200) or None (if still in progress)
    """
    access_token = cred_manager.get_access_token()
    response = http_request_with_reauth(
        cred_manager=cred_manager,
        url=poll_url,
        retry_count=3,
        request_type="GET",
        allowed_methods=["GET"],
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
