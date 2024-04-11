from typing import List
from typing import Literal

import requests

from app.cloud.core import BaseCredentialManager
from app.transport import http_request_with_retry


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
