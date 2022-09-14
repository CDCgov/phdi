from typing import List


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
        for entry in bundle.get("entry", [])
        if entry.get("resource", {}).get("resourceType", "") == resource_type
    ]


def get_field(resource: dict, field: str, use: str, default_field: int = 0) -> str:
    """
    Find the first-occuring instance of the field in a given FHIR-
    formatted JSON dict, such that the instance is associated with
    a particular "use" case of a given field (such as name or address).
    Use case here refers to the FHIR-based usage of classifying how
    a value is used in reporting. For example, find the first name
    for a patient that has a "use" of "official" (meaning the name
    is used for official reports). If no instance of a field with
    the requested use case can be found, instead return a specified
    default value for the field.

    :param resource: A FHIR-formatted resource
    :param field: The field to extract
    :param use: The 'use' the field must have to qualify
    :param default_field: (optional) The index of the field type to treat as
      the default return type if no field with the requested use case is
      found; if not supplied, use the first data available
    :return: The first instance of the field value matching the desired
      use, or a default field value if a match couldn't be found
    """
    if field == "":
        raise ValueError("Field must be a defined, non-empty string")
    if use == "":
        raise ValueError("Use must be a defined, non-empty string")
    if field not in resource:
        raise KeyError(f"Given resource does not contain a key called {field}")

    # The next function returns the "next" (in our case first) item from an
    # iterator that meets a given condition; if non exist, we index the
    # field for a default value
    try:
        return next(
            (item for item in resource.get(field, []) if item.get("use") == use),
            resource.get(field)[default_field],
        )
    except Exception:
        raise IndexError(
            "Index of provided field default is beyond length of field array"
        )


def get_one_line_address(address: dict) -> str:
    """
    Extract a one-line string representation of an address from a
    JSON dictionary holding address information.

    :param address: The address bundle
    :return: A one-line string representation of an address
    """
    if len(address) == 0:
        return ""
    raw_one_line = " ".join(address.get("line", []))
    raw_one_line += f" {address.get('city', '')}, {address.get('state', '')}"
    if address.get("postalCode", "") != "":
        raw_one_line += f" {address['postalCode']}"
    return raw_one_line
