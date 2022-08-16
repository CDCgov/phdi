import logging
import requests

from requests.adapters import HTTPAdapter
from typing import List, Literal
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
    Carryout an HTTP Request using a specific retry strategy. Essentially
    a wrapper function around the retry strategy implementation of a
    mounted HTTP request.

    :param url: The url at which to make the HTTP request
    :param retry_count: The number of times to re-try the request, if the
      first attempt fails
    :param request_type: The type of request to be made. Currently supports
      GET and POST.
    :param allowed_methods: The list of allowed HTTP request methods (i.e.
      POST, PUT, etc.) for the specific URL and query
    :param headers: JSON-type dictionary of headers to make the request with,
      including Authorization and content-type
    :param data: JSON data in the case that the request requires data to be
      posted. Defaults to none.
    :raises ValueError: An unsupported request_type is passed
    :return: A requests.Response object with the outcome of the http request
    """
    # Configure the settings of the 'requests' session we'll make
    # the API call with
    retry_strategy = Retry(
        total=retry_count,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=allowed_methods,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)

    # Now, actually try to complete the API request
    if request_type == "POST":
        try:
            response = http.post(
                url=url,
                headers=headers,
                json=data,
            )
        except Exception:
            # TODO: Potentially remove logging, and replace with reported errors.
            logging.exception(f"POST request to {url} failed.")
            return
    elif request_type == "GET":
        try:
            response = http.get(
                url=url,
                headers=headers,
            )
            return response
        except Exception:
            # TODO: Potentially remove logging, and replace with reported errors.
            logging.exception(f"GET request to {url} failed.")
    else:
        raise ValueError(f"Unexpected request_type {request_type}")

    return response
