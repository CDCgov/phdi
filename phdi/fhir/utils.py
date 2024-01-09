import json
import random
from functools import cache
from typing import Any
from typing import Callable
from typing import List
from typing import Literal
from typing import Union

import fhirpathpy

selection_criteria_types = Literal["first", "last", "random", "all"]


def apply_selection_criteria(
    value: List[Any],
    selection_criteria: selection_criteria_types,
) -> str | List:
    """
    Returns value(s), according to the selection criteria, from a given list of values
    parsed from a FHIR resource. A single string value is returned - if the selected
    value is a complex structure (list or dict), it is converted to a string.
    :param value: A list containing the values parsed from a FHIR resource.
    :param selection_criteria: A string indicating which element(s) of a list to select.
    :return: Value(s) parsed from a FHIR resource that conform to the selection
      criteria.
    """

    if selection_criteria == "first":
        value = value[0]
    elif selection_criteria == "last":
        value = value[-1]
    elif selection_criteria == "random":
        value = random.choice(value)
    elif selection_criteria == "all":
        return value
    else:
        raise ValueError(
            f'Selection criteria {selection_criteria} is not a valid option. Must be one of "first", "last", "random", or "all".'  # noqa
        )

    # Temporary hack to ensure no structured data is written using pyarrow.
    # Currently Pyarrow does not support mixing non-structured and structured data.
    # https://github.com/awslabs/aws-data-wrangler/issues/463
    # Will need to consider other methods of writing to parquet if this is an essential
    # feature.
    if type(value) is dict:  # pragma: no cover
        value = json.dumps(value)
    elif type(value) is list:
        value = ",".join(value)
    return value


def extract_value_with_resource_path(
    resource: dict,
    path: str,
    selection_criteria: Literal["first", "last", "random", "all"] = "first",
) -> Union[Any, None]:
    """
    Yields a single value from a resource based on a provided `fhir_path`.
    If the path doesn't map to an extant value in the first, returns
    `None` instead.
    :param resource: The FHIR resource to extract a value from.
    :param path: The `fhir_path` at which the value can be found in the
      resource.
    :param selection_criteria: A string dictating which value to extract,
      if multiple values exist at the path location.
    :return: The extracted value, or `None` if the value doesn't exist.
    """
    parse_function = get_fhirpathpy_parser(path)
    value = parse_function(resource)
    if len(value) == 0:
        return None
    else:
        value = apply_selection_criteria(value, selection_criteria)
        return value


def find_entries_by_resource_type(bundle: dict, resource_type: str) -> List[dict]:
    """
    Collect all entries of a specific type in a bundle of FHIR data and
    return references to them in a list.

    :param bundle: The FHIR bundle to search for resource entries.
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
    Finds an instance of the specified field in a given FHIR- formatted JSON dictionary.
    Optionally, a particular "use" of a field can be provided such that only instances
    with that purpose are considered. For example, find the name for a patient that has
    a "use" of "official". "Use" here refers to the FHIR-based usage of classifying a
    value's purpose. If no instance of a field with the requested use case can be found,
    instead return a specified default value for the field.

    :param resource: A FHIR-formatted resource.
    :param field: The field to extract.
    :param index: The nth element of the field to return. If the index is greater than
      the number of elements in the field, the last element will be returned. If the
      index is less than 1, the first element will be returned. Default: 1.
    :param use: The 'use' the field must have to qualify for selection. Default: None.
    :param require_use: If True and no elements of the specified field have that
      use, none will be returned. If False and no elements of the specified field have
      that use, the nth element as indicated by the index parameter will be returned.
      This parameter is ignored if no use is specified. Default: True.
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


@cache
def get_fhirpathpy_parser(fhirpath_expression: str) -> Callable:
    """
    Accepts a FHIRPath expression, and returns a callable function
    which returns the evaluated value at fhirpath_expression for
    a specified FHIR resource.
    :param fhirpath_expression: The FHIRPath expression to evaluate.
    :return: A function that, when called passing in a FHIR resource,
      will return value at `fhirpath_expression`.
    """
    return fhirpathpy.compile(fhirpath_expression)


def get_one_line_address(address: dict) -> str:
    """
    Extracts a one-line string representation of an address from a
    JSON dictionary holding address information.

    :param address: The FHIR-formatted address.
    :return: A one-line string representation of an address.
    """
    if len(address) == 0:
        return ""
    raw_one_line = " ".join(address.get("line", []))
    raw_one_line += f" {address.get('city', '')}, {address.get('state', '')}"
    if address.get("postalCode", ""):
        raw_one_line += f" {address['postalCode']}"
    return raw_one_line
