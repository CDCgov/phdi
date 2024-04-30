from typing import List
from typing import Literal

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry


def http_request_with_retry(
    url: str,
    retry_count: int,
    request_type: Literal["GET", "POST"],
    allowed_methods: List[str],
    headers: dict,
    data: dict = None,
) -> requests.Response:
    """
    Executes an HTTP request, retrying the request if the returned HTTP status code
    is one of a specified list of codes.

    :param url: The url at which to make the HTTP request.
    :param retry_count: The number of times to retry the request, if the
      first attempt fails.
    :param request_type: The type of request to be made. Currently supports
      GET and POST.
    :param allowed_methods: The list of allowed HTTP request methods (i.e.,
      POST, PUT) for the specific URL and query.
    :param headers: JSON-type dictionary of headers to make the request with,
      including Authorization and content-type.
    :param data: The data as a JSON-formatted dictionary, used when the request
      requires data to be posted. Default: `None`
    :raises ValueError: An unsupported HTTP method (e.g., PATCH, DELETE) was passed
      to the request_type parameter.
    :return: A HTTP request response.
    """

    request_type = request_type.upper()
    if request_type not in ["GET", "POST"]:
        raise ValueError(
            f"The HTTP '{request_type}' method is not currently supported."
        )

    # Configure the settings of the 'requests' session we'll make
    # the API call with
    retry_strategy = Retry(
        total=retry_count,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=allowed_methods,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("http://", adapter)
    http.mount("https://", adapter)

    # Now, actually try to complete the API request
    # TODO: Condense this down to make a single call using
    # http.request(method=request_type, url=url, headers=headers, json=data)
    if request_type == "POST":
        response = http.post(
            url=url,
            headers=headers,
            json=data,
        )
    elif request_type == "GET":
        response = http.get(
            url=url,
            headers=headers,
        )

    return response
