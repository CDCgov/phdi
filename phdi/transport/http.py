import requests

from requests.adapters import HTTPAdapter
from requests.models import Response
from typing import List, Literal, Union
from urllib3 import Retry


def _generate_custom_response(
    url: str, status_code: int, content: Union[str, bytes]
) -> requests.Response:
    """
    Returns a custom requests.Response object with relevant information about the
    request and why it failed. The primary purpose of this functionality is to mock a
    Response object in instances where the requests.request method fails or was not
    executed in order to provide consistency in functionality that expects a Response
    object to be returned.

    :param url: The URL of the request that failed or was never run.
    :param status_code: The HTTP status code that should be returned to the user.
    :param content: Relevant information about why the original request failed or
    wasn't run. This could include the Exception, the traceback info, or a custom
    message. It should be passed as a string in the form of a dictionary
    (e.g. '{"exception": "<class 'requests.exceptions.ConnectTimeout'>})')
    """
    response = Response()
    response.url = url
    response.status_code = status_code
    # Response._content requires the text to be bytes instead of unicode
    response._content = content.encode() if isinstance(content, str) else content
    return response


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
        except Exception as e:
            content = f'{{"message": "POST request to {url} failed with the following exception: {type(e)}"}}'  # noqa
            response = _generate_custom_response(
                url=url, status_code=500, content=content
            )
    elif request_type == "GET":
        try:
            response = http.get(
                url=url,
                headers=headers,
            )
        except Exception:
            content = f'{{"message": "GET request to {url} failed with the following exception: {type(e)}"}}'  # noqa
            response = _generate_custom_response(
                url=url, status_code=500, content=content
            )
    else:
        content = f'{{"message": "The {request_type} HTTP method is not currently supported"}}'  # noqa
        response = _generate_custom_response(url=url, status_code=400, content=content)

    return response
