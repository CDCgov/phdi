import fhirpathpy
import json
import random
import pathlib

from functools import cache
from typing import Any, Callable, Literal, List
from urllib.parse import parse_qs, urlencode

from phdi.cloud.core import BaseCredentialManager
from phdi.fhir.transport import fhir_server_get
from phdi.tabulation.tables import load_schema, write_table


def _apply_selection_criteria(
    value: List[Any],
    selection_criteria: Literal["first", "last", "random"],
) -> str:
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

    # Temporary hack to ensure no structured data is written using pyarrow.
    # Currently Pyarrow does not support mixing non-structured and structured data.
    # https://github.com/awslabs/aws-data-wrangler/issues/463
    # Will need to consider other methods of writing to parquet if this is an essential
    # feature.
    if type(value) == dict:  # pragma: no cover
        value = json.dumps(value)
    elif type(value) == list:
        value = ",".join(value)
    return value


def apply_schema_to_resource(resource: dict, schema: dict) -> dict:
    """
    Creates and returns a dictionary of data based on a FHIR resource
    and a schema. The keys of the created dict are the "new names"
    for the fields in the given schema, and the values are the
    elements of the given resource that correspond to these fields.
    Here, `new_name` is a property contained in the schema that
    specifies what a particular variable should be called. If a
    schema can't be found for the given resource type, the raw
    resource is instead returned.

    :param resource: A FHIR resource on which to apply a schema.
    :param schema: A schema specifying the desired values to extract,
      by FHIR resource type.
    :return: A dictionary of data with the desired values, as specified by the schema.
    """

    data = {}
    resource_schema = schema.get(resource.get("resourceType", ""))
    if resource_schema is None:
        return data

    for field in resource_schema.keys():
        path = resource_schema[field]["fhir_path"]

        parse_function = _get_fhirpathpy_parser(path)
        value = parse_function(resource)

        if len(value) == 0:
            data[resource_schema[field]["new_name"]] = ""  # pragma: no cover
        else:
            selection_criteria = resource_schema[field]["selection_criteria"]
            value = _apply_selection_criteria(value, selection_criteria)
            data[resource_schema[field]["new_name"]] = str(value)

    return data


def tabulate_data(extracted_data: dict, schema: dict) -> List[List]:
    """
    Turns data extracted from a FHIR server into a tabular format for
    downstream processing. Accepts a schema to apply to the extracted
    data, which is transformed into a list of lists. The first entry
    in the returned list is a list of headers for the new table, and
    subsequent lists are each an extracted data element represented
    in a tabular format.

    :param extracted_data: The content response from the FHIR server
      holding retrieved data to tabulate.
    :param schema: The schema of columns and values to apply to the
      extracted data.
    :return: A list of lists of the extracted data representing a
      table. The first list in the return value is a list of headers
      serving as the columns, and all subsequent lists are rows in
      the table.
    """

    data = []
    headers = None
    for resource in extracted_data.get("entry", []):
        values_from_resource = apply_schema_to_resource(
            resource.get("resource", {}), schema
        )

        # apply_schema_to_resource ensures that all desired table fields
        # exist in the first element
        if headers == None:
            headers = sorted(list(values_from_resource.keys()))
            data.append(headers)

        # use extracted headers to tabulate each row in the same order
        if values_from_resource != {}:
            tabulated_values = [values_from_resource[h] for h in headers]
            data.append(tabulated_values)

    return data


def generate_table(
    schema: dict,
    output_path: pathlib.Path,
    output_format: Literal["parquet"],
    fhir_url: str,
    cred_manager: BaseCredentialManager,
) -> None:
    """
    Makes a table for a single schema.

    :param schema: A schema specifying the desired values, by FHIR resource type.
    :param output_path: A path specifying where the table should be written.
    :param output_format: A string indicating the file format to be used.
    :param fhir_url: A URL to a FHIR server.
    :param cred_manager: The credential manager used to authenticate to the FHIR server.
    """
    output_path.mkdir(parents=True, exist_ok=True)
    for resource_type in schema:

        output_file_name = output_path / f"{resource_type}.{output_format}"

        # TODO: make _count (and other query parameters) configurable
        query = f"/{resource_type}?_count=1000"
        url = fhir_url + query

        writer = None
        next_page = True
        while next_page:
            response = fhir_server_get(url, cred_manager)
            if response.status_code != 200:
                break

            # Load queried data.
            query_result = json.loads(response.content)
            data = []

            # Extract values specified by schema from each resource.
            # values_from_resource is a dictionary of the form:
            # {field1:value1, field2:value2, ...}.

            for resource in query_result["entry"]:
                values_from_resource = apply_schema_to_resource(
                    resource["resource"], schema
                )
                if values_from_resource != {}:
                    data.append(values_from_resource)

            # Write data to file.
            writer = write_table(data, output_file_name, output_format, writer)

            # Check for an additional page of query results.
            for link in query_result.get("link"):
                if link.get("relation") == "next":
                    url = link.get("url")
                    break
                else:
                    next_page = False

        if writer is not None:
            writer.close()


def generate_all_tables_in_schema(
    schema_path: pathlib.Path,
    base_output_path: pathlib.Path,
    output_format: Literal["parquet"],
    fhir_url: str,
    cred_manager: BaseCredentialManager,
) -> None:
    """
    Queries a FHIR server for information, and generates and stores the tables in the
    desired location, according to the supplied schema.

    :param schema_path: A path to the location of a YAML schema config file.
    :param base_output_path: A path to the directory where tables of the schema should
      be written.
    :param output_format: The file format of the tables to be generated.
    :param fhir_url: The URL to a FHIR server.
    :param cred_manager: The credential manager used to authenticate to the FHIR server.
    """

    schema = load_schema(schema_path)

    for table in schema.keys():
        output_path = base_output_path / table
        generate_table(
            schema[table], output_path, output_format, fhir_url, cred_manager
        )


@cache
def _get_fhirpathpy_parser(fhirpath_expression: str) -> Callable:
    """
    Accepts a FHIRPath expression, and returns a callable function which returns the
    evaluated value at fhirpath_expression for a specified FHIR resource.

    :param fhirpath_expression: The FHIRPath expression to evaluate.
    :return: A function that, when called passing in a FHIR resource, will return value
      at `fhirpath_expression`.
    """
    return fhirpathpy.compile(fhirpath_expression)


def _generate_search_url(
    url_with_querystring: str, default_count: int = None, default_since: str = None
) -> str:
    """
    Generates a FHIR query string using the supplied search string, defaulting values
    for `_count` and `_since`, if given and not already set in the
    `url_with_querystring`.

    :param url_with_querystring: The search URL with querystring. The search URL
      may contain the base URL, or may start with the resource name.
    :param default_count: If set, and querystring does not specify `_count`, the
      `_count` parameter is added to the query string with this value. Default: `None`
    :param default_since: If set, and querystring does not specify `_since`, the
      `_since` parameter is added to the query string with this value. Default: `None`
    :return: The `url_with_querystring` including any defaulted values.
    """
    if "?" in url_with_querystring:
        search_url_prefix, search_query_string = url_with_querystring.split("?", 1)
    else:
        # Split will generate a ValueError if the delimiter is not found
        # in the string, so handle this as an edge case.
        search_url_prefix, search_query_string = (url_with_querystring, "")

    query_string_dict = parse_qs(search_query_string)
    if default_count is not None and query_string_dict.get("_count") is None:
        query_string_dict["_count"] = [default_count]

    if default_since is not None and query_string_dict.get("_since") is None:
        query_string_dict["_since"] = [default_since]

    updated_query_string = urlencode(query_string_dict, doseq=True)
    if not updated_query_string:
        return search_url_prefix

    return "?".join((search_url_prefix, urlencode(query_string_dict, doseq=True)))
