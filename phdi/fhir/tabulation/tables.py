import fhirpathpy
import json
import random
import pathlib

from functools import cache
from typing import Any, Callable, Dict, Literal, List, Union, Tuple
from urllib.parse import parse_qs, urlencode

from phdi.cloud.core import BaseCredentialManager
from phdi.fhir.transport import fhir_server_get, http_request_with_reauth
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
    :param schema: A user-defined schema describing, for one or more
      tables, the indexing FHIR resource type used to define rows, as
      well as some number of columns specifying what values to include.
    A schema specifying the desired values to extract,
      by FHIR resource type.
    :return: A dictionary of data with the desired values, as
      specified by the schema.
    """

    data = {}
    for table_name, table in schema.get("tables", {}).items():
        resource_type = table.get("resource_type", "")

        if resource_type == "":
            raise ValueError(
                "Each table must specify resource_type. "
                + f"resource_type not found in table {table_name}."
            )

        # We only care about the parts of the schema that match the resource
        if resource.get("resourceType", "") == resource_type:
            for column_name, column in table.get("columns", {}).items():
                col_in_table = column_name.lower().strip().replace(" ", "_")

                # Use FHIR-path to identify desired value
                path = column["fhir_path"]
                parse_function = _get_fhirpathpy_parser(path)
                value = parse_function(resource)

                if len(value) == 0:
                    data[col_in_table] = ""

                else:
                    selection_criteria = column["selection_criteria"]
                    value = _apply_selection_criteria(value, selection_criteria)
                    data[col_in_table] = str(value)

    return data


def tabulate_data(data: List[dict], schema: dict) -> dict:
    """
    Transforms a list of bundle entries into a tabular format (given by
    a list of lists) using a user-defined schema of the columns of
    interest. Tabulation works using a two-pass procedure.

    First, resources that are associated with one another in the
    provided schema (identified by the presence of a `reference_location`
    field in one of the schema's columns) are grouped together.
    For each table, one type of resource serves as the "anchor",
    which defines the number of rows in the table, while referenced
    resources are either "forwards" or "reverse" references, depending
    on their relationship to the anchor type.

    Second, the aggregated resources are parsed for value extraction
    using the schema's columns, and the results are stored in a list of
    lists for that table. The first entry in this list are the headers
    of the data, taken from the schema. This procedure is performed
    for each table defined in the schema.

    :param data: A list of FHIR bundle entries to tabulate.
    :param schema: A user-defined schema describing, for one or more
      tables, the indexing FHIR resource type used to define rows, as
      well as some number of columns specifying what values to include.
    :return: A dictionary mapping table names to lists of lists.
      The first list in the return value is a list of headers
      serving as the columns, and all subsequent lists are rows in
      the table.
    """

    # First pass: build mapping of references for easy lookup
    ref_directions = _get_reference_directions(schema)
    ref_dicts = _build_reference_dicts(data, ref_directions)

    tabulated_data = {}
    for table_name, table_params in schema.get("tables", {}).items():
        # Get the columns from the schema so we always iterate through
        # them in a consistent order
        column_items = table_params.get("columns", {}).items()
        headers = [column_name for column_name, _ in column_items]
        tabulated_data[table_name] = [headers]
        anchor_type = (
            schema.get("tables", {}).get(table_name, {}).get("resource_type", "")
        )

        # Second pass over just the anchor data, since that
        # defines the table's rows
        for anchor_resource, is_result_because in (
            ref_dicts.get(table_name, {}).get(anchor_type, {}).values()
        ):

            # Resources that aren't matches to the original criteria
            # don't generate rows because they were included via a
            # reference
            if is_result_because != "match":
                continue

            row = []

            for _, column_params in column_items:
                path_to_use = column_params["fhir_path"]
                resource_to_use = anchor_resource

                # Determine if we need to make a lookup in our
                # first-pass reference mapping
                if "reference_location" in column_params:
                    resource_to_use = _dereference_included_resource(
                        resource_to_use,
                        path_to_use,
                        anchor_resource,
                        column_params,
                        ref_dicts,
                        table_name,
                    )
                    if resource_to_use is None:
                        row.append(None)
                        continue

                # Forward pointers are many-to-one anchor:target (i.e. many patients
                # could point to the same general practitioner), so we only need a
                # single value for them
                if isinstance(resource_to_use, dict):
                    row.append(
                        _extract_value_with_resource_path(
                            resource_to_use,
                            path_to_use,
                            column_params["selection_criteria"],
                        )
                    )

                # Reverse pointers are one-to-many (one patient could have multiple
                # observations pointing to them), so they need to be stored in a list
                else:
                    values = [
                        _extract_value_with_resource_path(
                            r, path_to_use, column_params["selection_criteria"]
                        )
                        for r in resource_to_use
                    ]
                    row.append(values)

            tabulated_data[table_name].append(row)

    # Drop invalid values specified in the schema
    tabulated_data = drop_invalid(tabulated_data, schema)

    return tabulated_data


def generate_table(
    schema: dict,
    output_path: pathlib.Path,
    output_format: Literal["parquet"],
    fhir_url: str,
    cred_manager: BaseCredentialManager,
) -> None:
    """
    Makes a table for a single schema.

    :param schema: A user-defined schema describing, for one or more
      tables, the indexing FHIR resource type used to define rows, as
      well as some number of columns specifying what values to include.
    :param output_path: A path specifying where the table should be written.
    :param output_format: A string indicating the file format to be used.
    :param fhir_url: A URL to a FHIR server.
    :param cred_manager: The credential manager used to authenticate to the FHIR server.
    """
    output_path.mkdir(parents=True, exist_ok=True)
    for table in schema.get("tables", {}).values():
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

    for table in schema.get("tables", {}).values():
        output_path = base_output_path / table.get("resourceType")
        generate_table(schema, output_path, output_format, fhir_url, cred_manager)


@cache
def _get_fhirpathpy_parser(fhirpath_expression: str) -> Callable:
    """
    Accepts a FHIRPath expression, and returns a callable function
    which returns the evaluated value at fhirpath_expression for
    a specified FHIR resource.

    :param fhirpath_expression: The FHIRPath expression to evaluate.
    :return: A function that, when called passing in a FHIR resource,
      will return value at `fhirpath_expression`.
    """
    return fhirpathpy.compile(fhirpath_expression)


def _get_reference_directions(schema: dict) -> dict:
    """
    Creates a dictionary mapping indicating how the resources that
    will be used in creating the final output tables relate to each
    other. For any column desired in an output table, it is possible
    for the column to be found in a resource that either a) references
    a given resource, or b) is referenced by the given resource.
    Since each table in the schema is defined with an "anchor" resource
    (the main type of resource determining the number of rows in the
    table), referenced resources of type A can be labeled "backward"
    pointers and referenced resources of type B can be labeled "forward"
    pointers. This mapping is used to efficiently group and aggregate
    related resource data for tabulation.

    :param schema: A user-defined schema describing, for one or more
      tables, the indexing FHIR resource type used to define rows, as
      well as some number of columns specifying what values to include.
    :return: A dictionary containing mappings, for each table, of
      how referenced resources relate to the anchor resource.
    """

    directions_by_table = {}
    for table_name, table_params in schema.get("tables", {}).items():
        anchor_type = table_params.get("resource_type", "")
        directions_by_table[table_name] = {
            "anchor": anchor_type,
            "forward": set(),
            "reverse": {},
        }

        for column_params in table_params.get("columns", {}).values():
            if "reference_location" in column_params:
                [direction, ref_path] = column_params.get(
                    "reference_location", ""
                ).split(":", 1)
                referenced_resource_type = column_params.get("fhir_path", "").split(
                    "."
                )[0]
                if direction == "forward":
                    directions_by_table[table_name][direction].add(
                        referenced_resource_type
                    )
                else:
                    directions_by_table[table_name][direction][
                        referenced_resource_type
                    ] = ref_path

    return directions_by_table


def _extract_value_with_resource_path(
    resource: dict,
    path: str,
    selection_criteria: Literal["first", "last", "random"] = "first",
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
    parse_function = _get_fhirpathpy_parser(path)
    value = parse_function(resource)
    if len(value) == 0:
        return None
    else:
        value = _apply_selection_criteria(value, selection_criteria)
        return value


def _build_reference_dicts(data: List[dict], directions_by_table: dict) -> dict:
    """
    Groups resources previously determined to reference each other into
    dictionaries accessed using resource IDs. For each table, a dictionary
    is created whose keys are the ID of the anchor resource that the
    referenced resources relate to, and whose values are pointers to the
    referenced resources. This allows the `tabulate_data` function to
    simply iterate through the anchor resources (which are rows in the
    table) and use its ID to quickly fetch all related resources for
    columnar value extraction. This function and the `_get_reference_directions`
    function represent the "first pass" of the tabulate function's two-pass
    process.

    :param data: A list of FHIR bundle entries to tabulate.
    :param directions_by_table: The output of the `_get_reference_directions`
      function, which provides the directionality of linked resources to
      the anchors they reference.
    :return: A dictionary holding, for each table, the groups of resources
      from which column values will be extracted.
    """

    # Build up connections table by table, since one resource could be
    # used in multiple different tables
    reference_dicts = {}
    for table_name in directions_by_table.keys():
        reference_dicts[table_name] = {}

    for entry in data:
        resource = entry.get("resource", {})
        current_resource_type = resource.get("resourceType", "")

        # Check each resource we got back against each table's schema
        # to see if it slots in as an anchor, a forward reference, or
        # a reverse reference
        for table_name, resource_directions in directions_by_table.items():
            if (
                current_resource_type == resource_directions["anchor"]
                or current_resource_type in resource_directions["forward"]
            ):
                if current_resource_type not in reference_dicts[table_name]:
                    reference_dicts[table_name][current_resource_type] = {}

                # Forward pointers are easy: just use the resource's ID, since
                # that's what the anchor will reference; store as a tuple since
                # it's possible for an anchor resource to reference another
                # resource of the same type without the reference needing
                # to generate a row
                reference_dicts[table_name][current_resource_type][
                    resource.get("id", "")
                ] = (resource, entry.get("search", {}).get("mode", ""))

            if current_resource_type in resource_directions["reverse"]:
                if current_resource_type not in reference_dicts[table_name]:
                    reference_dicts[table_name][current_resource_type] = {}

                # Reverse pointers are more involved: need to figure out what
                # resource this points to
                ref_loc = directions_by_table[table_name]["reverse"][
                    current_resource_type
                ]
                ref_path = ref_loc.replace(":", ".") + ".reference"
                referenced_anchor = _extract_value_with_resource_path(
                    resource, ref_path
                )

                # There could be a many-to-one relationship with reverse pointers,
                # so store them in a list
                if (
                    referenced_anchor is not None
                    and referenced_anchor
                    not in reference_dicts[table_name][current_resource_type]
                ):
                    reference_dicts[table_name][current_resource_type][
                        referenced_anchor
                    ] = []
                reference_dicts[table_name][current_resource_type][
                    referenced_anchor
                ].append(resource)

    return reference_dicts


def _dereference_included_resource(
    resource_to_use: dict,
    path_to_use: str,
    anchor_resource: dict,
    column_params: dict,
    ref_dicts: dict,
    table_name: str,
) -> Union[dict, None]:

    anchor_id = anchor_resource.get("id", "")
    [direction, ref_path] = column_params["reference_location"].split(":", 1)
    referenced_type = path_to_use.split(".")[0]

    # If a reference resource is requested but the extracted
    # data didn't contain any of them, the referenced type
    # doesn't appear in the mapping
    if referenced_type not in ref_dicts[table_name]:
        return None

    # An anchor resource references another resource, so get the
    # ID from the anchor and look it up
    if direction == "forward":
        path_to_reference = ref_path.replace(":", ".") + ".reference"
        referenced_id = _extract_value_with_resource_path(
            anchor_resource, path_to_reference
        )

        # The requested resource may not exist
        if referenced_id not in ref_dicts[table_name][referenced_type]:
            return None
        resource_to_use = ref_dicts[table_name][referenced_type][referenced_id][0]

    # Another resource references our anchor resource
    else:
        if anchor_id not in ref_dicts[table_name][referenced_type]:
            return None
        resource_to_use = ref_dicts[table_name][referenced_type][anchor_id]

    return resource_to_use


def extract_data_from_fhir_search_incremental(
    search_url: str, cred_manager: BaseCredentialManager = None
) -> Tuple[List[dict], str]:
    """
    Performs a FHIR search for a single page of data and returns a dictionary containing
    the data and a next URL. If there is no next URL (this is the last page of data),
    then return None as the next URL.

    :param search_url: The URL to a FHIR server with search criteria.
    :param cred_manager: The credential manager used to authenticate to the FHIR server.
    :return: Tuple containing single page of data as a list of dictionaries and the next
        URL.
    """

    # TODO: Modify fhir_server_get (and http_request_with_reauth) to function without
    # mandating a credential manager. Then replace the direct call to
    # http_request_with_reauth with fhir_server_get.
    # response = fhir_server_get(url=full_url, cred_manager=cred_manager)
    response = http_request_with_reauth(
        url=search_url,
        cred_manager=cred_manager,
        retry_count=2,
        request_type="GET",
        allowed_methods=["GET"],
        headers={},
    )

    next_url = None
    for link in response.get("link", []):
        if link.get("relation") == "next":
            next_url = link.get("url")

    content = response.get("entry")

    return content, next_url


def extract_data_from_fhir_search(
    search_url: str, cred_manager: BaseCredentialManager = None
) -> List[dict]:
    """
    Performs a FHIR search, continuously using the "next" url to perform
    search continuations until no additional search results are available.
    Returns a dictionary containing the data from all search responses.

    :param search_url: The URL to a FHIR server with search criteria.
    :param cred_manager: The credential manager used to authenticate to the FHIR server.
    :return: A list of FHIR resources returned from the search.
    """

    results, next = extract_data_from_fhir_search_incremental(
        search_url=search_url, cred_manager=cred_manager
    )

    while next is not None:
        incremental_results, next = extract_data_from_fhir_search_incremental(
            search_url=next, cred_manager=cred_manager
        )
        results.extend(incremental_results)

    return results


def extract_data_from_schema(
    schema: dict, fhir_url: str, cred_manager: BaseCredentialManager = None
) -> Dict[str, List[dict]]:
    """
    Performs a full FHIR search for each table in `schema`, and returns a dictionary
    mapping the table name to corresponding search results.

    :param schema: The schema that defines the extraction to perform.
    :param cred_manager: The credential manager used to authenticate to the FHIR server.
    :return: A dictionary mapping table name to a list of FHIR resources returned from
      the search.
    """

    search_urls = _generate_search_urls(schema=schema)

    results = {}
    for table_name, search_url in search_urls.items():
        results[table_name] = extract_data_from_fhir_search(
            search_url=f"{fhir_url}/{search_url}", cred_manager=cred_manager
        )

    return results


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


def _merge_include_query_params_for_location(
    query_params: dict, reference_location: str
) -> dict:
    """
    Merges an _include and/or _revinclude search parameter into the supplied
    query parameters based on the supplied reference location.
    :param query_params: A dictionary containing query parameters of the form
      `{ "param_name": "param_value" }` or
      `{ "param_name": ["param_value1", ...]}`.
    :param reference_location: The FHIR resource type and field location for
      the referenced resource. For more informaiton see the
      [FHIR documentation](https://www.hl7.org/fhir/search.html#revinclude).
    :return: The modified `query_params` input parameter. Since the
      `query_params` dict is modified in place, the caller can access the
      result in the original input parameter if called with a variable
      or the return value.
    """

    if reference_location == "":
        raise ValueError("reference_location cannot be empty")

    direction, field_location = reference_location.split(":", 1)

    # Search term is _include for forward searchs, _revinclude for reverse searches.
    # In addition, we must add an :iterate modifier if the reference is relative to
    # another included resource
    query_param_name = None
    if direction == "forward":
        query_param_name = "_include"
    elif direction == "reverse":
        query_param_name = "_revinclude"

    current_referenced_direction = query_params.get(query_param_name)

    # Handle the case where the search term (_include or _revinclude)
    # is not specified or is specified as a list.
    if current_referenced_direction is None:
        current_referenced_direction = []
        query_params[query_param_name] = current_referenced_direction
    elif isinstance(current_referenced_direction, str):
        # Convert current_referenced_direction from str to list, and
        # make sure the query_params dict references the new object.
        current_referenced_direction = [current_referenced_direction]
        query_params[query_param_name] = current_referenced_direction

    if field_location not in current_referenced_direction:
        current_referenced_direction.append(field_location)

    return query_params


def _generate_search_urls(schema: dict) -> dict:
    """
    Parses a schema, and populates a dictionary containing generated search strings
    for each table, in the following structure:
    * table_1: search_string_1
    * table_2: search_string_2
    * ...

    :param schema: A user-defined schema describing, for one or more
      tables, the indexing FHIR resource type used to define rows, as
      well as some number of columns specifying what values to include.
    :raises ValueError: If any table does not contain a `search_string` entry.
    :return: A dictionary containing search URLs.
    """
    url_dict = {}

    schema_metadata = schema.get("metadata", {})
    count_top = schema_metadata.get("results_per_page")
    since_top = schema_metadata.get("earliest_update_datetime")

    for table_name, table in schema.get("tables", {}).items():
        resource_type = table.get("resource_type")

        if not resource_type:
            raise ValueError(
                "Each table must specify resource_type. "
                + f"resource_type not found in table {table_name}."
            )

        query_params = table.get("query_params", {})

        # Handle any includes specified in the columns
        for column in table.get("columns", {}).values():
            if "reference_location" in column:
                query_params = _merge_include_query_params_for_location(
                    query_params, column.get("reference_location", "")
                )

        search_string = resource_type
        if query_params is not None and len(query_params) > 0:
            search_string += f"?{urlencode(query_params)}"

        count = table.get("results_per_page", count_top)
        since = table.get("earliest_update_datetime", since_top)

        url_dict[table_name] = _generate_search_url(search_string, count, since)

    return url_dict


def drop_invalid(data: Dict, schema: Dict) -> List[list]:
    """
    Removes resources from tabulated data if the resource contains an invalid value, as
    specified in the invalid_values field in a user-defined schema. Users may provide
    invalid values as a list, including empty string values ("") and
    None/null values (null).

    :param data: A dictionary mapping table names to lists of lists. The first list in
        the data value is a list of headers serving as the columns, and all subsequent
        lists are rows in the table.
    :param schema: A schema of columns and values to apply to the
      tabulated data, including invalid_values if applicable.
    :param return: A dictionary mapping table names to lists of lists, without resources
        that contained invalid values. The first list in the data value is a list of
        headers serving as the columns, and all subsequent lists are rows in the table.
    """
    invalid_values_by_column_index = {}
    for table in schema.get("tables"):
        # Identify columns to drop invalid values for each table in schema
        columns = schema["tables"][table]["columns"]
        # Identify indices in List of Lists to check for invalid values
        invalid_values_by_column_index[table] = {
            i: columns[col].get("invalid_values")
            for i, col in enumerate(columns)
            if columns[col].get("invalid_values", [])
        }

    # Check if resource contains invalid values to be dropped
    for table in data.keys():
        if len(invalid_values_by_column_index[table]) > 0:
            for resource in data[table][1:]:
                for index, invalid_values in invalid_values_by_column_index[
                    table
                ].items():
                    if resource[index] in invalid_values:
                        data[table].remove(resource)
                        break

    return data
