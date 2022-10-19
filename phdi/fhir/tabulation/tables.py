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
    and a schema. The given schema should define a table for each
    resource type to-be-processed, and each such table must have a
    list of columns to be included in the table as well as a FHIR-path
    like object to access the value from the FHIR resource. The keys
    of the returned dictionary are the lower-cased, underscore-replaced
    names of the columns entered in the schema.

    :param resource: A FHIR resource on which to apply a schema.
    :param schema: A schema specifying the desired values to extract,
      by FHIR resource type.
    :return: A dictionary of data with the desired values, as
      specified by the schema.
    """

    data = {}
    for table_name, table in schema.get("tables", {}).items():
        resource_type = table.get("resource_type")

        if not resource_type:
            raise ValueError(
                "Each table must specify resource_type. "
                + f"resource_type not found in table {table_name}."
            )

        # We only care about the schema that matches the resource
        if resource.get("resourceType", "") == resource_type:
            for field in table.get("columns", []).keys():
                col_in_table = field.lower().strip().replace(" ", "_")

                # Use FHIR-path to identify desired value
                path = table["columns"][field]["fhir_path"]
                parse_function = _get_fhirpathpy_parser(path)
                value = parse_function(resource)

                if len(value) == 0:
                    data[col_in_table] = ""

                else:
                    selection_criteria = table["columns"][field]["selection_criteria"]
                    value = _apply_selection_criteria(value, selection_criteria)
                    data[col_in_table] = str(value)
            break

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
        if headers is None:
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
    for _, table in schema.get("tables", {}).items():
        resource_type = table.get("resource_type")
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

    for _, table in schema.get("tables", {}).items():
        output_path = base_output_path / table.get("resourceType")
        generate_table(schema, output_path, output_format, fhir_url, cred_manager)


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


def _generate_search_urls(schema: dict) -> dict:
    """
    Parses a schema, and populates a dictionary containing generated search strings
    for each table, in the following structure:
    * table_1: search_string_1
    * table_2: search_string_2
    * ...

    :param schema: The schema to parse and create search_strings.
    :raises ValueError: If any table does not contain a `search_string` entry.
    :return: A dictionary containing search URLs.
    """
    url_dict = {}

    count_top = schema.get("incremental_query_count")
    since_top = schema.get("earliest_update_datetime")

    for table_name, table in schema.get("tables", {}).items():
        resource_type = table.get("resource_type")

        if not resource_type:
            raise ValueError(
                "Each table must specify resource_type. "
                + f"resource_type not found in table {table_name}."
            )

        query_params = table.get("query_params")
        search_string = resource_type
        if query_params is not None and len(query_params) > 0:
            search_string += f"?{urlencode(query_params)}"

        count = table.get("incremental_query_count", count_top)
        since = table.get("earliest_update_datetime", since_top)

        url_dict[table_name] = _generate_search_url(search_string, count, since)

    return url_dict


def drop_null(response: list, schema_columns: dict):
    """
    Removes resources from a FHIR response if the resource contains a
    null value for fields where include_nulls is False, as specified
    in the schema.

    :param response: List of resources returned from FHIR API.
    :param schema_columns: Dictionary of columns to include in tabulation
      that specifies which columns should include_nulls.
    :param return: List of resources with removed nulls.
    """

    # Identify fields to drop nulls
    nulls_to_drop = [
        schema_columns[column]["new_name"]
        for column in schema_columns.keys()
        if not schema_columns[column]["include_nulls"]
    ]

    # Identify indices in List of Lists to check for nulls
    indices_of_nulls = [response[0].index(field) for field in nulls_to_drop]

    # Check if resource contains nulls to be dropped
    for resource in response[1:]:
        # Check if any of the fields are none
        for i in indices_of_nulls:
            if resource[i] == "":
                response.remove(resource)
                break
    return response
