from dataclasses import replace
from fastapi import FastAPI, Response, status
import fhirpathpy
from pydantic import BaseModel, Field
from typing import Optional, Literal, List, Union, Callable, Any, Dict
import urllib.parse
import datetime
from pathlib import Path
from phdi.cloud.core import BaseCredentialManager
import json
import random

from phdi.tabulation.tables import validate_schema, write_data
from phdi.fhir.tabulation.tables import (
    _generate_search_urls,
    extract_data_from_fhir_search_incremental,
)
from app.config import get_settings
from app.utils import get_cred_manager, search_for_required_values

# Read settings from environmnent.
get_settings()

# Instantiate FastAPI and set metadata.
description = Path("description.md").read_text()
app = FastAPI(
    title="PHDI Tabulation Service",
    version="0.0.1",
    contact={
        "name": "CDC Public Health Data Infrastructure",
        "url": "https://cdcgov.github.io/phdi-site/",
        "email": "dmibuildingblocks@cdc.gov",
    },
    license_info={
        "name": "Creative Commons Zero v1.0 Universal",
        "url": "https://creativecommons.org/publicdomain/zero/1.0/",
    },
    description=description,
)


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


def drop_invalid(data: List[list], schema: Dict, table_name: str) -> List[list]:
    """
    Removes resources from tabulated data if the resource contains an invalid value, as
    specified in the invalid_values field in a user-defined schema. Users may provide
    invalid values as a list, including empty string values ("") and
    None/null values (null).
    :param data: A list of lists containing data for a table. The first list in
        the data value is a list of headers serving as the columns, and all subsequent
        lists are rows in the table.
    :param schema: A declarative, user-defined specification, for one or more tables,
        that defines the metadata, properties, and columns of those tables as they
        relate to FHIR resources.
    :param table_name: Name of the table to drop invalid values.
    :param return: A list of lists, without rows of data derived from the FHIR
        resources and elements that contained invalid values.
        The first list in the data value is a list of headers serving as the
        columns, and all subsequent lists are rows in the table.
    """
    invalid_values_by_column_index = {}

    # Identify columns to drop invalid values for each table in schema
    columns = schema["tables"][table_name]["columns"]
    # Identify indices in List of Lists to check for invalid values
    invalid_values_by_column_index[table_name] = {
        i: columns[col].get("invalid_values")
        for i, col in enumerate(columns)
        if columns[col].get("invalid_values", [])
    }

    # Check if resource contains invalid values to be dropped
    rows_to_remove = []
    if len(invalid_values_by_column_index) > 0:
        for i in range(len(data)):
            for index, invalid_values in invalid_values_by_column_index[
                table_name
            ].items():
                if data[i][index] in invalid_values:
                    rows_to_remove.append(i)
                    break

    # Remove rows with invalid values
    for idx, i in enumerate(rows_to_remove):
        del data[i - idx]

    return data


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
        return None  # pragma: no cover

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


def tabulate_data(data: List[dict], schema: dict, table_name: str) -> List[list]:
    """
    Transforms a list of FHIR bundle resource entries into a tabular
    format (given by a list of lists) using a user-defined schema.
    Tabulation works using a two-pass procedure. First, resources
    that are associated with one another in the provided schema
    (identified by the presence of a `reference_location` field in
    one of the schema's columns) are grouped together. For each
    table, one type of resource serves as the "anchor", which
    defines the number of rows in the table, while referenced
    resources are either "forwards" or "reverse" references,
    depending on their relationship to the anchor type. Second,
    the aggregated resources are parsed for value extraction using
    the schema's columns, and the results are stored in a list of
    lists for that table. The first entry in this list are the headers
    of the data, taken from the schema. This functions performs the
    above procedure on one table from the schema, specified by a
    table name.
    :param data: A list of FHIR bundle resource entries to tabulate.
    :param schema: A declarative, user-defined specification, for one or more tables,
        that defines the metadata, properties, and columns of those tables as they
        relate to FHIR resources.
    :param table_name: A string specifying the name of a table defined
      in the given schema.
    :raises KeyError: If the given `table_name` does not occur in the
      provided schema.
    :return: A list of lists denoting the tabulated form of the data.
      The first list is a list of headers serving as the columns,
      and all subsequent lists are rows in the table.
    """

    if table_name not in schema.get("tables", {}):
        raise KeyError(f"Provided table name {table_name} not found in schema")

    # First pass: build mapping of references for easy lookup
    ref_directions = _get_reference_directions(schema)
    ref_dicts = _build_reference_dicts(data, ref_directions)

    # Get the columns from the schema so we always iterate through
    # them in a consistent order
    table_params = schema["tables"][table_name]
    column_items = table_params["columns"].items()
    headers = [column_name for column_name, _ in column_items]
    tabulated_data = [headers]
    anchor_type = schema["tables"][table_name]["resource_type"]

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
        tabulated_data.append(row)

    # Drop invalid values specified in the schema
    tabulated_data = drop_invalid(tabulated_data, schema, table_name)

    return tabulated_data


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
    :param schema: A user-defined schema, for one or more tables, that
        maps a FHIR resource and element to a specified column in a table.
    :return: A dict containing mappings, for each table, of
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


def _build_reference_dicts(data: List[dict], directions_by_table: dict) -> dict:
    """
    Groups resources previously determined to reference each other into
    dictionaries accessed using resource IDs. For each table, a dictionary
    is created whose keys are the ID of the anchor resource that the
    referenced resources relate to, and whose values are pointers to the
    referenced resources. This allows the `tabulate_data` function to
    simply iterate through the anchor resources (which are rows in the
    table) and use its ID to quickly fetch all related resources for
    columnar value extraction.
    :param data: A list of FHIR bundle resource entries to tabulate.
    :param directions_by_table: The output of the `_get_reference_directions`
      function, which provides the directionality of linked resources to
      the anchors they reference.
    :return: A dict holding, for each table, the groups of resources
      from which column values will be extracted.
    """

    # Build up connections table by table, since one resource could be
    # used in multiple different tables
    reference_dicts = {}
    for table_name in directions_by_table.keys():
        reference_dicts[table_name] = {}
    count = 0
    for entry in data:

        resource = entry.get("resource", {})
        current_resource_type = resource.get("resourceType", "")
        if current_resource_type == "Observation":
            count += 1

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
                referenced_anchor = referenced_anchor.split("/")[-1]

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
    print("Count:", count)
    return reference_dicts


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


class TabulateInput(BaseModel):
    """
    Request schema for the tabulate endpoint.
    """

    schema_: dict = Field(alias="schema", description="A JSON formatted PHDI schema.")
    output_type: Literal["parquet", "csv", "sql"] = Field(
        description="Method for persisting data after extraction from the FHIR server "
        "and tabulation."
    )
    schema_name: Optional[str] = Field(
        description="Name of the schema, if not provided here then it must be included "
        "within the metadata section of the schema in the 'schema_name' key."
    )
    fhir_url: Optional[str] = Field(
        description="The URL of the FHIR server from which data should be extracted, "
        "should end with '/fhir'. If not provided here then it must be set as an "
        "environment variable."
    )
    cred_manager: Optional[Literal["azure", "gcp"]] = Field(
        description="Chose a PHDI credential manager to use for authentication with the"
        " FHIR. May be set here or as an environment variable. If not provided anywhere"
        " then un-authenticated FHIR server requests will be attempted."
    )

    # _check_schema_validity = validator("schema_", allow_reuse=True)(
    # validate_schema
    # )


@app.get("/")
async def health_check():
    """
    Check service status. If an HTTP 200 status code is returned along with
    '{"status": "OK"}' then the tabulation service is available and running properly.
    """
    return {"status": "OK"}


@app.post("/tabulate", status_code=200)
async def tabulate_endpoint(input: TabulateInput, response: Response):
    """
    This endpoint will extract, tabulate, and persist data from a FHIR server according
    to a user-defined schema in the method of the user's choosing.
    """

    # Look for values that must be provided in the request body, or set as environment
    # variables.
    input = dict(input)
    required_values = ["fhir_url"]
    search_result = search_for_required_values(input, required_values)
    if search_result != "All values were found.":
        response.status_code = status.HTTP_400_BAD_REQUEST
        return search_result

    # Look for a schema name.
    if input["schema_name"] is None:
        input["schema_name"] = input["schema_"]["metadata"].get("schema_name")
        if input["schema_name"] is None:
            response.status_code = status.HTTP_400_BAD_REQUEST
            response_message = "A value for schema_name could not be found. A value for"
            "schema_name must be provided using the 'schema_name' key in the request"
            "body, or within the metadata section of the schema."
            return response_message

    # Instantiate a credential manager.
    if input["cred_manager"] is not None:
        input["cred_manager"] = get_cred_manager(
            cred_manager=input["cred_manager"], location_url=input["fhir_url"]
        )

    return tabulate(**input)


def tabulate(
    schema_: dict,
    output_type: Literal["parquet", "csv", "sql"],
    schema_name: Optional[str],
    fhir_url: str,
    cred_manager: BaseCredentialManager = None,
) -> dict:
    """
    Given a schema and FHIR server, extract the required data from the FHIR server,
    tabulate the data according to the schema, and persist the data according to the
    file type specified by output_type.

    :param schema_: A declarative, user-defined specification, for one or more tables,
        that defines the metadata, properties, and columns of those tables as they
        relate to FHIR resources. Additional information about creating and using these
        schema can be found at
        https://github.com/CDCgov/phdi/blob/main/tutorials/tabulation-tutorial.md.
    :output_type: Specifies how the data should be persisted after it has been extracted
        from a FHIR server and tabulated.
    :schema_name: The name for the schema.
    :fhir_url: The URL of the FHIR server data should be extracted from.
    :cred_manager: A credential manager that can be used handle authentication with FHIR
        server.
    """
    # Load search_urls to query FHIR server
    search_urls = _generate_search_urls(schema=schema_)
    directory = (
        Path()
        / "tables"
        / schema_name
        / datetime.datetime.now().strftime("%m-%d-%YT%H%M%S")
    )

    directory.mkdir(parents=True)
    for table_name, search_url in search_urls.items():
        next = search_url
        pq_writer = None
        print(table_name)
        while next is not None:
            # Return set of incremental results and next URL to query
            incremental_results, next = extract_data_from_fhir_search_incremental(
                search_url=urllib.parse.urljoin(fhir_url, search_url),
                cred_manager=cred_manager,
            )
            print(urllib.parse.urljoin(fhir_url, search_url))
            # Tabulate data for set of incremental results
            tabulated_incremental_data = tabulate_data(
                incremental_results, schema_, table_name
            )
            # Write set of tabulated incremental data
            write_data(
                tabulated_data=tabulated_incremental_data,
                directory=str(directory),
                filename=filename,
                output_type=output_type,
                db_file=schema_name,
                db_tablename=table_name,
                pq_writer=pq_writer,
            )

        if pq_writer is not None:
            pq_writer.close()

    result = {
        "schema_name": schema_name,
        "output_type": output_type,
        "fhir_url": fhir_url,
        "tables": list(search_urls.keys()),
        "directory": str(directory),
    }
    return result
