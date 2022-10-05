from typing import Any, List


def find_entries_by_resource_type(bundle: dict, resource_type: str) -> List[dict]:
    """
    Collect all entries of a specific type in a bundle of FHIR data and
    return references to them in a list.

    :param bundle: The FHIR bundle to search for entries.
    :param resource_type: The type of FHIR resource to find.
    :return: A list holding all entries of the requested resource type that were
      found in the input bundle.
    """
    return [
        entry
        for entry in bundle.get("entry", [])
        if entry.get("resource", {}).get("resourceType", "") == resource_type
    ]


def get_field(
    resource: dict,
    field: str,
    index: int = 1,
    use: str = None,
    require_use: bool = True,
) -> Any:
    """
    Finds the first-occurring instance of the field in a given
    FHIR-formatted JSON dict, such that the instance is associated with
    a particular "`use`" of a given field (such as name or address).
    `Use` here refers to the FHIR-based usage of classifying how
    a value is used in reporting. For example, finds the first name
    for a patient that has a "`use`" of "`official`" (meaning the name
    is used for official reports). If no instance of a field with
    the requested use case can be found, it instead returns the specified
    default value for the field.

    :param resource: A FHIR-formatted resource.
    :param field: The field to extract.
    :param use: The `use` the field must have to qualify.
    :param default_field: The index of the field type to treat as
      the default return type if no field with the requested use case is
      found. Default: first data available, regardless of `use`.
    :return: The first instance of the field value matching the desired
      use, or a default field value if a match couldn't be found.
    """
    # TODO revisit the `default_field` logic, and confirm this is the best way to handle
    # choosing a default
    if field == "":
        raise ValueError("The field parameter must be a defined, non-empty string.")
    if use == "":
        raise ValueError(
            "The use parameter should be a defined, non-empty string. If you don't want to include a use, set the parameter to None."  # noqa
        )
    if field not in resource:
        raise KeyError(f"This resource does not contain a field called {field}.")

    elements = resource.get(field, [])
    if use is not None:
        elements_with_use = [item for item in elements if item.get("use") == use]
        if len(elements_with_use) == 0 and require_use:
            return None
        if len(elements_with_use) > 0:
            elements = elements_with_use

    # min(...) ensures index <= len(elements) and the -1 shifts back to 0-index
    # max(...) ensures the index is not negative
    index = max(min(index, len(elements)) - 1, 0)

    return elements[index] if len(elements) > 0 else None


def get_one_line_address(address: dict) -> str:
    """
    Extracts a one-line string representation of an address from a
    JSON dictionary holding address information.

    :param address: The FHIR-formatted address bundle.
    :return: A one-line string representation of an address.
    """
    if len(address) == 0:
        return ""
    raw_one_line = " ".join(address.get("line", []))
    raw_one_line += f" {address.get('city', '')}, {address.get('state', '')}"
    if address.get("postalCode", ""):
        raw_one_line += f" {address['postalCode']}"
    return raw_one_line
