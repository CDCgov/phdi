from typing import List, Dict, Union


def find_entries_by_resource_type(bundle: dict, resource_type: str) -> List[dict]:
    """
    Collect all entries of a specific type in a bundle of FHIR data and
    return references to them in a list.

    :param bundle: The FHIR bundle to find patients in
    :param resource_type: The type of FHIR resource to find
    :return: List holding all entries of the requested resource type that were
      found in the input bundle
    """
    return [
        entry
        for entry in bundle.get("entry")
        if entry.get("resource", {}).get("resourceType") == resource_type
    ]


def get_field(
    resource: dict,
    field: str,
    index: int = 0,
    use: str = None,
    require_use: bool = True,
) -> Union[Dict, List, str, None]:
    """
    Find the first-occuring instance of the field in a given FHIR-
    formatted JSON dict. Optionally, a particular "use" case of a
    given field (such as name or address), can be provided such that
    only instances with that use case are considered. Use case here
    refers to the FHIR-based usage of classifying how a value is used
    in reporting. For example, find the first name for a patient that
    has a "use" of "official" (meaning the name is used for official
    reports). If no instance of a field with the requested use case
    can be found, instead return a specified default value for the field.

    :param resource: Resource from a FHIR bundle
    :param field: The field to extract
    :param index: (optional) The nth element of the field to return. Note that the index
    starts at 0, not 1. If the index is greater than the number of elements in the
    field, the last element will be returned. Defaults to returning the first element.
    :param use: (optional) The 'use' the field must have to qualify for selection
    :param require_use: (optional) Indicates if the 'use' is required. If True, then
    if no elements of the specified field have that use, none will be returned. If
    False, then if no elements of the specified field have that use the default index
    will be returned. This parameter is ignored if no use is specified.
    :return: The first instance of the field value matching the desired
      use, or a default field value if a match couldn't be found
    """
    if field == "":
        raise ValueError("Field must be a defined, non-empty string")
    if field not in resource:
        raise KeyError(f"This resource does not contain a field called {field}")

    elements = resource.get(field, [])
    if use is not None:
        elements_with_use = [item for item in elements if item.get("use") == use]
        if len(elements_with_use) == 0 and require_use:
            return None
        if len(elements_with_use) > 0:
            elements = elements_with_use

    index = -1 if index >= len(elements) else index
    return elements[index] if len(elements) > 0 else None


def get_one_line_address(address: dict) -> str:
    """
    Extract a one-line string representation of an address from a
    JSON dictionary holding address information.

    :param address: The address bundle
    :return: A one-line string representation of an address
    """
    raw_one_line = " ".join(address.get("line", []))
    raw_one_line += f" {address.get('city')}, {address.get('state')}"
    if address.get("postalCode", ""):
        raw_one_line += f" {address['postalCode']}"
    return raw_one_line
