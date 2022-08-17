from typing import List


def find_resource_by_type(bundle: dict, resource_type: str) -> List[dict]:
    """
    Collect all resources of a specific type in a bundle of FHIR data and
    return references to them in a list.

    :param bundle: The FHIR bundle to find patients in
    :param resource_type: The type of FHIR resource to find
    :return: List holding all resources of the requested type that were
      found in the input bundle
    """
    return [
        resource
        for resource in bundle.get("entry")
        if resource.get("resource").get("resourceType") == resource_type
    ]


# @TODO: Improve this function for more general use, since it's user-
# facing (i.e. make it more robust, less fragile, etc.)
def get_field(resource: dict, field: str, use: str, default_field: int) -> str:
    """
    For a given field (such as name or address), find the first-occuring
    instance of the field in a given FHIR-formatted JSON dict, such that
    the instance is associated with a particular "use" case of the field
    (use case here refers to the FHIR-based usage of classifying how a
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
    :return: The first instance of the field value matching the desired
      use, or a default field value if a match couldn't be found
    """
    # The next function returns the "next" (in our case first) item from an
    # iterator that meets a given condition; if non exist, we index the
    # field for a default value
    return next(
        (item for item in resource[field] if item.get("use") == use),
        resource[field][default_field],
    )


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
