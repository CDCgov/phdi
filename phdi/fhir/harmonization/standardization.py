import copy
from typing import List, Literal, Union
from phdi.harmonization import (
    standardize_name,
    standardize_country_code,
    standardize_phone,
)


def standardize_names(
    data: dict,
    trim: bool = True,
    case: Literal["upper", "lower", "title"] = "upper",
    remove_numbers: bool = True,
    overwrite: bool = True,
) -> dict:
    """
    Standardizes all names contained in a given FHIR bundle or a FHIR resource. The
    default standardization behavior is our defined non-numeric, space-trimming, full
    capitalization standardization, but other modes may be specified.

    :param data: A FHIR-formatted JSON dict.
    :param trim: Whether leading/trailing whitespace should be removed. Default: `True`
    :param case: The type of casing that should be used. Default: `upper`
    :param remove_numbers: If true, delete numeric characters; if false leave numbers
      in place. Default: `True`
    :param overwrite: If true, `data` is modified in-place;
      if false, a copy of `data` modified and returned.  Default: `True`
    :return: The bundle or resource with names appropriately standardized.
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
    Standardizes all phone numbers in a given FHIR bundle or a FHIR resource.
    Standardization is done according to the underlying `standardize_phone` function in
    `phdi.harmonization`.

    :param data: A FHIR bundle or FHIR-formatted JSON dict.
    :param overwrite: If true, `data` is modified in-place;
      if false, a copy of `data` modified and returned.  Default: `True`
    :return: The bundle or resource with phones appropriately standardized.
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


def _standardize_names_in_resource(
    resource: dict,
    trim: bool = True,
    case: Literal["upper", "lower", "title"] = "upper",
    remove_numbers: bool = True,
    overwrite: bool = True,
) -> dict:
    """
    Standardizes all found names in a given resource.
    The resource can be of any type currently supported by the
    function's logic. At this time, those resources include:

    * Patient

    The parameters to this function match the standardization flags
    used by the underlying `standardize_name` function found in
    `phdi.harmonization`. For more information, see the docstring for
    that function.

    :param resource: A FHIR-formatted JSON dictionary.
    :param trim: Whether leading/trailing whitespace should be removed. Default: `True`
    :param case: The type of casing that should be used. Default: `upper`
    :param remove_numbers: Whether to delete numeric characters. Default: `True`
    :param overwrite: Whether to replace the original names in the input
      data with the standardized names. Default: `True`
    :return: The resource with appropriately standardized names.
    """

    if not overwrite:
        resource = copy.deepcopy(resource)

    if resource.get("resourceType", "") == "Patient":
        for name in resource.get("name", []):

            # Handle family names
            if "family" in name:
                transformed_name = standardize_name(
                    name.get("family", ""), trim, case, remove_numbers
                )
                name["family"] = transformed_name

            # Given names are stored in a list, as there could be multiple,
            # process them all and take the overall diff for metrics
            if "given" in name:
                transformed_names = [
                    standardize_name(g, trim, case, remove_numbers)
                    for g in name.get("given", [])
                ]
                name["given"] = transformed_names
    return resource


def _standardize_phones_in_resource(
    resource: dict, overwrite=True
) -> Union[dict, None]:

    if not overwrite:
        resource = copy.deepcopy(resource)

    if resource.get("resourceType", "") == "Patient":
        for telecom in resource.get("telecom", []):
            if telecom.get("system") == "phone" and "value" in telecom:
                countries = _extract_countries_from_resource(resource)
                transformed_phone = standardize_phone(
                    telecom.get("value", ""), countries
                )
                telecom["value"] = transformed_phone
    return resource


def _extract_countries_from_resource(
    resource: dict, code_type: Literal["alpha_2", "alpha_3", "numeric"] = "alpha_2"
) -> List[str]:
    """
    Builds a list containing all of the countries, standardized by code_type, in the
    addresses of a given FHIR resource as interpreted by the ISO 3611: standardized
    country identifier. If the resource is not of a supported type, no
    countries will be returned. Currently supported resource types are:

    * Patient

    :param resource: A FHIR-formatted JSON dictionary.
    :param code_type: A string equal to 'alpha_2', 'alpha_3', or 'numeric'
      to specify which type of standard country identifier to generate.
      Default: `alpha_2`
    :return: A list of all the standardized countries found in the resource's
      addresses.
    """
    countries = []
    resource_type = resource.get("resourceType")
    if resource_type == "Patient":
        for address in resource.get("address"):
            country = address.get("country")
            if country:
                countries.append(standardize_country_code(country, code_type))
    return countries
