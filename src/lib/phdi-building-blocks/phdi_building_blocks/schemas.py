import csv
import pathlib
import os
import yaml
import json
import random
from typing import Literal, List, Union
import pyarrow as pa
import pyarrow.parquet as pq
import fhirpathpy
from pathlib import Path

from phdi_building_blocks.fhir import fhir_server_get


def load_schema(path: str) -> dict:
    """
    Given the path to local YAML files containing a user-defined schema read the file
    and return the schema as a dictionary.

    :param path: Path specifying the location of a YAML file containing a schema.
    :return schema: A user-defined schema
    """
    try:
        with open(path, "r") as file:
            schema = yaml.safe_load(file)
        return schema
    except FileNotFoundError:
        return {}


def apply_selection_criteria(
    value: list,
    selection_criteria: Literal["first", "last", "random", "all"],
) -> Union[str, List[str]]:
    """
    Given a list of values parsed from a FHIR resource, return value(s) according to the
    selection criteria. In general a single value is returned, but when
    selection_criteria is set to "all" a list containing all of the parsed values is
    returned.

    :param value: A list containing the values parsed from a FHIR resource.
    :param selection_criteria: A string indicating which element(s) of a list to select.
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
    if type(value) == dict:
        value = json.dumps(value)
    elif type(value) == list:
        value = ",".join(value)
    return value


def apply_schema_to_resource(resource: dict, schema: dict) -> dict:
    """
    Given a resource and a schema, return a dictionary with values of the data
    specified by the schema and associated keys defined by the variable name provided
    by the schema.

    :param resource: A FHIR resource on which to apply a schema.
    :param schema: A schema specifying the desired values by FHIR resource type.
    """

    data = {}
    resource_schema = schema.get(resource.get("resourceType", ""))
    if resource_schema is None:
        return data
    for field in resource_schema.keys():
        path = resource_schema[field]["fhir_path"]
        value = fhirpathpy.evaluate(resource, path)

        if len(value) == 0:
            data[resource_schema[field]["new_name"]] = ""
        else:
            selection_criteria = resource_schema[field]["selection_criteria"]
            value = apply_selection_criteria(value, selection_criteria)
            data[resource_schema[field]["new_name"]] = value

    return data


def make_table(
    schema: dict,
    output_path: pathlib.Path,
    output_format: Literal["parquet"],
    fhir_url: str,
    access_token: str,
):
    """
    Given the schema for a single table, make the table.

    :param schema: A schema specifying the desired values by FHIR resource type.
    :param output_path: A path specifying where the table should be written.
    :param output_format: A string indicating the file format to be used.
    :param fhir_url: URL to a FHIR server.
    :param access_token: Bear token to authenticate with the FHIR server.
    """
    output_path.mkdir(parents=True, exist_ok=True)
    for resource_type in schema:

        output_file_name = output_path / f"{resource_type}.{output_format}"

        query = f"/{resource_type}"
        url = fhir_url + query

        writer = None
        next_page = True
        while next_page:
            response = fhir_server_get(url, access_token)
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
            writer = write_schema_table(data, output_file_name, output_format, writer)

            # Check for an additional page of query results.
            for link in query_result.get("link"):
                if link.get("relation") == "next":
                    url = link.get("url")
                    break
                else:
                    next_page = False

        if writer is not None:
            writer.close()


def make_schema_tables(
    schema_path: pathlib.Path,
    base_output_path: pathlib.Path,
    output_format: Literal["parquet"],
    fhir_url: str,
    access_token: str,
):
    """
    Given the url for a FHIR server, the location of a schema file, and and output
    directory generate the specified schema and store the tables in the desired
    location.

    :param schema_path: A path to the location of a YAML schema config file.
    :param base_output_path: A path to the directory where tables of the schema should
    be written.
    :param output_format: Specifies the file format of the tables to be generated.
    :param fhir_url: URL to a FHIR server.
    :param access_token: Bear token to authenticate with the FHIR server.
    """

    schema = load_schema(schema_path)

    for table in schema.keys():
        output_path = base_output_path / table
        make_table(schema[table], output_path, output_format, fhir_url, access_token)


def write_schema_table(
    data: List[dict],
    output_file_name: pathlib.Path,
    file_format: Literal["parquet"],
    writer: pq.ParquetWriter = None,
):
    """
    Write data extracted from the FHIR Server to a file.

    :param data: A list of dictionaries specifying the data for each row of a table
    where the keys of each dict correspond to the columns, and the values contain the
    data for each entry in a row.
    :param output_file_name: Full name for the file where the table is to be written.
    :param output_format: Specifies the file format of the table to be written.
    :param writer: A writer object that can be kept open between calls of this function
    to support file formats that cannot be appended to after being written
    (e.g. parquet).
    """

    if file_format == "parquet":
        table = pa.Table.from_pylist(data)
        if writer is None:
            writer = pq.ParquetWriter(output_file_name, table.schema)
        writer.write_table(table=table)
        return writer

    if file_format == "csv":
        keys = data[0].keys()
        new_file = False if os.path.isfile(output_file_name) else True
        with open(output_file_name, "a", newline="") as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            if new_file:
                dict_writer.writeheader()
            dict_writer.writerows(data)


def print_schema_summary(
    schema_directory: pathlib.Path,
    display_head: bool = False,
):
    """
    Given a directory containing tables of the specified file format, print a summary of
    each table.

    :param schema_directory: Path specifying location of schema tables.
    :param display_head: Print the head of each table when true. Note depending on the
    file format this may require reading large amounts of data into memory.
    """
    for (directory_path, _, file_names) in os.walk(schema_directory):
        for file_name in file_names:
            if file_name.endswith("parquet"):
                # Read metadata from parquet file without loading the actual data.
                parquet_file = pq.ParquetFile(Path(directory_path) / file_name)
                print(parquet_file.metadata)

                # Read data from parquet and convert to pandas data frame.
                if display_head is True:
                    parquet_table = pq.read_table(Path(directory_path) / file_name)
                    df = parquet_table.to_pandas()
                    print(df.head())
                    print(df.info())
            if file_name.endswith("csv"):
                with open(file_name, "r") as csv_file:
                    reader = csv.reader(csv_file, dialect="excel")
                    print(next(reader))
                    return "hi"
