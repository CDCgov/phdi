from typing import List, Union
from urllib3 import Retry
import requests
from requests.adapters import HTTPAdapter
import logging


def find_resource_by_type(bundle: dict, resource_type: str) -> List[dict]:
    """
    Collect all resources of a specific type in a bundle of FHIR data and
    return references to them in a list.

    :param bundle: The FHIR bundle to find patients in
    :param resource_type: The type of FHIR resource to find
    """
    return [
        resource
        for resource in bundle.get("entry")
        if resource.get("resource").get("resourceType") == resource_type
    ]


def get_one_line_address(address: dict) -> str:
    """
    Extract a one-line string representation of an address from a
    JSON dictionary holding address information.

    :param address: The address bundle
    """
    raw_one_line = " ".join(address.get("line", []))
    raw_one_line += f" {address.get('city')}, {address.get('state')}"
    if "postalCode" in address and address["postalCode"]:
        raw_one_line += f" {address['postalCode']}"
    return raw_one_line


def get_field(resource: dict, field: str, use: str, default_field: int) -> str:
    """
    For a given field (such as name or address), find the first-occuring
    instance of the field in a given patient JSON dict, such that the
    instance is associated with a particular "use" case of the field (use
    case here refers to the FHIR-based usage of classifying how a
    value is used in reporting). For example, find the first name for a
    patient that has a "use" of "official" (meaning the name is used
    for official reports). If no instance of a field with the requested
    use case can be found, instead return a specified default field.

    :param resource: Resource from a FHIR bundle
    :param field: The field to extract
    :param use: The use the field must have to qualify
    :param default_field: The index of the field type to treat as
        the default return type if no field with the requested use case is
        found
    """
    # TODO Determine if we need to implement .get() to ensure KeyErrors are not thrown
    # or if we want the KeyError functionality and thus just need to document that
    # behavior.

    # The next function returns the "next" (in our case first) item from an
    # iterator that meets a given condition; if non exist, we index the
    # field for a default value
    return next(
        (item for item in resource[field] if item.get("use") == use),
        resource[field][default_field],
    )


def standardize_text(raw_text: str, **kwargs) -> str:
    """
    Perform standardization on a provided text string, given a set of transformations.

    :param raw_text: The raw text string to standardize
    :param **kwargs: A series of transformations that should be applied to the text
    string. Only recognized transformations will be utilized; all other specified
    transformations will be ignore. The recognized transformations are as follows:
        - trim (Bool): Indicates if leading and trailing whitespace should be removed.
        - case (Literal["upper", "lower", "title"]): Defines what casing should be
        applied to the string.
        - remove_numbers (Bool): Indicates if numbers should removed from the string.
        - remove_punctuation (Bool): Indicates if characters that are not letters,
        numbers, nor spaces should be removed.
        - remove_characters (List[str]): Provides a list of characters that should be
        removed from the string.
    """

    # A certain order of operations needs to be imposed in order to make the output
    # deterministic, and as close to the user's intent as possible. While it may see
    # at first glance that this code could be cleaned up with a creative for loop,
    # the current understanding is that the fact that Python doesn't maintain the order
    # of keys in dictionaries, there's no easy to way to ensure that transformations are
    # processed in the appropriate way. An example of where this becomes an issue is
    # when the user makes the following call:
    #     standardize_text(" 123 hi 456 ", trim=True, remove_numbers=True)
    # Because dictionaries and kwargs are unordered in Python prior to version 3.6, the
    # outcome could either be "hi" or " hi ", depending on if numbers are removed prior
    # to stripping the string or not. As of Python 3.6, the order of **kwargs is
    # preserved, but we can't assume that the user will pass the parameters in the
    # proper order. All of this is to say that a series of if statements appears to be
    # the most straightforward means by which we can ensure that the transformations are
    # applied in the appropriate order.
    text = raw_text

    if "remove_numbers" in kwargs:
        text = "".join([ltr for ltr in text if not ltr.isnumeric()])
    if "remove_punctuation" in kwargs:
        text = "".join([ltr for ltr in text if ltr.isalnum() or ltr == " "])
    if "remove_characters" in kwargs:
        text = "".join([ltr for ltr in text if ltr not in kwargs["remove_characters"]])
    if "trim" in kwargs:
        text = text.strip()
    if "case" in kwargs:
        if kwargs["case"] == "upper":
            text = text.upper()
        if kwargs["case"] == "lower":
            text = text.lower()
        if kwargs["case"] == "title":
            text = text.title()

    return text


def http_request_with_retry(
    url: str,
    retry_count: int,
    request_type: str,
    allowed_methods: List[str],
    headers: dict,
    data: dict = None,
) -> Union[None, requests.Response]:
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
            logging.exception(
                "POST request to " + url + " failed for data: " + str(data)
            )
            return
    elif request_type == "GET":
        try:
            response = http.get(
                url=url,
                headers=headers,
            )
            return response
        except Exception:
            logging.exception("GET request to " + url + " failed.")

    return response
