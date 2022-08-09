from typing import Literal
import copy

from phdi.fhir.harmonization.standardization import (
    _standardize_names_in_resource,
    _standardize_phones_in_resource,
)


def standardize_names(
    data: dict,
    trim: bool = True,
    case: Literal["upper", "lower", "title"] = "upper",
    remove_numbers: bool = True,
    overwrite: bool = True,
) -> dict:
    """
    Given either a FHIR bundle or a FHIR resource, transform all names
    contained in any resource in the input.  The default standardization
    behavior is our defined non-numeric, space-trimming, full
    capitalization standardization, but other modes may be specified.

    :param data: Either a FHIR bundle or a FHIR-formatted JSON dict
    :param trim: Whether leading/trailing whitespace should be removed
    :param: case: The type of casing that should be used
    :param: remove_numbers: Whether to delete numeric characters
    :param overwrite: Whether to replace the original names in the input
      data with the standardized names (default is yes)
    :return: The bundle or resource with names appropriately standardized
    """
    # Copy the data if we don't want to overwrite the original
    if not overwrite:
        data = copy.deepcopy(data)

    # Allow users to pass in either a resource or a bundle
    bundle = data
    if "entry" not in data:
        bundle = {"entry": [{"resource": data}]}

    # Handle all resources individually
    for entry in bundle.get("entry"):
        resource = entry.get("resource", {})
        resource = _standardize_names_in_resource(
            resource, trim, case, remove_numbers, overwrite
        )

    if "entry" not in data:
        return bundle.get("entry", [{}])[0].get("resource", {})
    return bundle


def standardize_phones(data: dict, overwrite=True) -> dict:
    """
    Given a FHIR bundle or a FHIR resource, standardize all phone
    numbers contained in any resources in the input data.
    Standardization is done according to the underlying
    standardize_phone function in phdi.harmonization, so for more
    information on country-coding and parsing, see the relevant
    docstring.

    :param data: A FHIR bundle or FHIR-formatted JSON dict
    :param overwrite: Whether to replace the original phone numbers
      in the input data with the standardized versions (default is yes)
    :return: The bundle or resource with phones appropriately
      standardized
    """

    if not overwrite:
        data = copy.deepcopy(data)

    # Allow users to pass in either a resource or a bundle
    bundle = data
    if "entry" not in data:
        bundle = {"entry": [{"resource": data}]}

    for entry in bundle.get("entry"):
        resource = entry.get("resource", {})
        resource = _standardize_phones_in_resource(resource, overwrite)

    if "entry" not in data:
        return bundle.get("entry", [{}])[0].get("resource", {})
    return bundle
