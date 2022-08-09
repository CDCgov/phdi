from copy import copy
from typing import List, Literal, Union
from phdi.harmonization import (
    standardize_name,
    standardize_country_code,
    standardize_phone,
)


def _standardize_names_in_resource(
    resource: dict,
    trim: bool = True,
    case: Literal["upper", "lower", "title"] = "upper",
    remove_numbers: bool = True,
    overwrite: bool = True,
) -> Union[dict, None]:
    """
    Helper method to standardize all found names in a given resource.
    The resource can be of any type currently supported by the
    function's logic. At this time, those resources include:

      - Patient

    The parameters to this function match the standardization flags
    used by the underlying "standardize_name" function found in
    phdi.harmonization. For more information, see the docstring for
    that function.

    :param resource: A FHIR-formatted JSON dictionary
    :param trim: Whether to trim trailing/leading whitespace
    :param case: What case to employ for the cleaned name
    :param remove_numbers: Whether to delete numeric characters from
      names in the resource
    :param overwrite: Whether to overwrite the input data with the
      new, standardized value (default is yes)
    :return: The resource (or a copy thereof) with standardized
      information in place of the raw
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
    Given a FHIR resource, build a list containing all of the counries
    found in the addresses associated with that resource in a standardized
    form sepcified by code_type. If the resource is not of a supported
    type, no countries will be contained in the returned list. Currently
    supported resource types are:

    - Patient

    :param resource: A FHIR-formatted JSON dictionary
    :param code_type: A string equal to 'alpha_2', 'alpha_3', or 'numeric'
      to specify which type of standard country identifier to generate
    """
    countries = []
    resource_type = resource.get("resourceType")
    if resource_type == "Patient":
        for address in resource.get("address"):
            country = address.get("country")
            countries.append(standardize_country_code(country, code_type))
    return countries
