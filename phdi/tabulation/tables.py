import csv
import importlib.resources
import json
import os
import pathlib
import sqlite3 as sql
from typing import List
from typing import Literal
from typing import Union

import pyarrow as pa
import pyarrow.parquet as pq
import yaml
from jsonschema import validate


def load_schema(path: pathlib.Path) -> dict:
    """
    Given the path to a local YAML or JSON file containing a schema,
    loads the file and return the resulting schema as a dictionary.
    If the file can't be found, raises an error.

    :param path: The file path to a YAML file holding a schema.
    :raises ValueError: If the provided path points to an unsupported file type.
    :raises FileNotFoundError: If the file to be loaded could not be found.
    :raises JSONDecodeError: If a JSON file is provided with invalid JSON.
    :return: A dict representing a schema read from the given path.
    """
    try:
        with open(path, "r") as file:
            if path.suffix == ".yaml":
                schema = yaml.safe_load(file)
            elif path.suffix == ".json":
                schema = json.load(file)
            else:
                ftype = path.suffix.replace(".", "").upper()
                raise ValueError(f"Unsupported file type provided: {ftype}")
        validate_schema(schema)
        return schema
    except FileNotFoundError:
        raise FileNotFoundError(
            "The specified file does not exist at the path provided."
        )
    except json.decoder.JSONDecodeError as e:
        raise json.decoder.JSONDecodeError(
            "The specified file is not valid JSON.", e.doc, e.pos
        )


def validate_schema(schema: dict):
    """
    Validates the schema structure, ensuring all required schema elements are present
    and all schema elements are of the expected data type.

    :param schema: A declarative, user-defined specification, for one or more tables,
        that defines the metadata, properties, and columns of those tables as they
        relate to FHIR resources.
    :raises jsonschema.exception.ValidationError: If the schema is invalid.
    """
    # Load validation schema
    with importlib.resources.open_text(
        "phdi.tabulation", "validation_schema.json"
    ) as file:
        validation_schema = json.load(file)

    validate(schema=validation_schema, instance=schema)


def write_data(
    tabulated_data: List[List],
    directory: str,
    output_type: Literal["csv", "parquet", "sql"],
    filename: str = None,
    db_file: str = None,
    db_tablename: str = None,
    pq_writer: pq.ParquetWriter = None,
    schema: dict = None,
    table_name: str = None,
) -> Union[None, pq.ParquetWriter]:
    """
    Writes a set of tabulated data to a particular output format on disk
    (one of CSV, Parquet, or SQL). For CSV and Parquet writing, a filename
    must be provided to write output to. In the case of the SQL format,
    a database file (if one exists and is being modified) must be specified
    along with a table name in place of a filename. Creates new data files
    if the given options specify a file that doesn't exist, and appends
    data to already-present files if they do.

    :param tabulated_data: A list of lists in which the first element
      is the headers for the table-to-write and subsequent elements
      are rows in the table.
    :param directory: The directory in which to write the output data
      (if `output_type` is CSV or Parquet), or the directory in which
      the `db_file` is stored (if a database already exists) or should
      be created in (if a database does not already exist).
    :param output_type: The format the data should be written to.
    :param filename: The name of the CSV or Parquet file data should be
      written to. Omit if `output_type` is SQL. Default: `None`.
    :param db_file: The name of the database file to either create or
      access when writing to a SQL format. Omit if `output_type` is not
      SQL. Default: `None`.
    :param db_tablename: The name of the table in the database to create
      or write data to. Omit if `output_type` is not SQL. Default: `None`.
    :param pq_writer: A pre-existing `ParquetWriter` object that can be
      used to append data to a parquet format. Used in cases where
      incremental writing to a parquet destination is desired. Omit if
      `output_type` is not Parquet. Default: `None`.
    """
    # some elements may themselves contain lists, if selection_criteria = all is used
    for i in range(1, len(tabulated_data)):
        table_list = tabulated_data[i]
        for row, elt in enumerate(table_list):
            if isinstance(elt, list):
                tabulated_data[i][row] = _convert_list_to_string(elt)
            if isinstance(elt, dict):
                tabulated_data[i][row] = str(elt)

    if output_type == "csv":
        write_headers = (
            False if os.path.isfile(os.path.join(directory, filename)) else True
        )
        with open(os.path.join(directory, filename), "a", newline="") as fp:
            writer = csv.writer(fp, dialect="excel")
            if write_headers:
                writer.writerow(tabulated_data[0])
            writer.writerows(tabulated_data[1:])

    if output_type == "parquet":
        if schema and table_name:
            # Create the parquet schema based on the config file
            pq_schema = _create_pa_schema_from_table_schema(
                schema, tabulated_data[0], table_name
            )
        else:
            pq_schema = None
        # Rearrange data so that it is column, not row based as parquet needs
        parquet_data = _create_parquet_data(tabulated_data, pq_schema)
        if pq_schema:
            table = pa.Table.from_arrays(
                _create_from_arrays_data(parquet_data[1:]), schema=pq_schema
            )
        else:
            # If no schema file is provided, use the names field
            table = pa.Table.from_arrays(
                _create_from_arrays_data(parquet_data[1:]), names=tabulated_data[0]
            )
        if pq_writer is None:
            pq_writer = pq.ParquetWriter(
                os.path.join(directory, filename), table.schema
            )
        pq_writer.write_table(table=table)
        return pq_writer

    # @TODO:
    # 1. support username and passwords for database access
    # 2. figure out a more intelligent way to serialize data that's being
    # written to the SQL DB; there's the possibility that we need to write
    # list data to the table if an anchor has multiple reverse references,
    # but SQL can't write native python lists, so we need to either
    # stringify them, json.dumps serialize them, or binarize them
    if output_type == "sql":
        # We need a file-space cursor to operate on a connected table
        conn = sql.connect(os.path.join(directory, db_file))
        cursor = conn.cursor()

        # Create requested table if it's not already in the database
        headers = tuple(tabulated_data[0])
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {db_tablename} {headers};")

        # Format the programmatic values correctly by number of cols
        # Need this ugly construction so that the binding placeholder qmarks
        # don't have quotes around them individually when parsed by the SQL
        # engine
        hdr_placeholder = "({})".format(", ".join("?" * len(tabulated_data[0])))
        tuple_data = [tuple([str(x) for x in row]) for row in tabulated_data[1:]]
        # Have to do a format string this way to avoid an empty f-string error
        print(tuple_data)
        cursor.executemany(
            "INSERT INTO {} {} VALUES {};".format(
                db_tablename, headers, hdr_placeholder
            ),
            tuple_data,
        )

        conn.commit()
        conn.close()


def _convert_list_to_string(val: list) -> str:
    """
    Serializes a given list into a string, separating values with commas.

    :param val: A list that may contain other types of objects to be stringified
      for use in CSV, SQL, etc
    :return: A string representation of the list
    """
    for i, v in enumerate(val):
        if isinstance(v, list):
            val[i] = _convert_list_to_string(v)
        elif isinstance(v, dict):
            val[i] = str(v)
        elif not isinstance(v, str):
            val[i] = str(v)
    return (",").join(val)


def _create_pa_schema_from_table_schema(
    schema: dict, col_names: List, table_name: str
) -> pa.Schema:
    """
    Returns a parquet schema based on the schema definition file provided to the
      function. Defaults to String.

    :param schema: A dict value that is defined by the user which contains the structure
      of the data.
    :param col_names: A list of column names that the parquet schema is being generated
      for.
    :param table_name: A string of the table name that the parquet schema is being
      generated for.
    :return: A pyarrow schema object based on the schema of the table, column names, and
      which table is being used.
    """
    table_columns = schema["tables"][table_name]["columns"]
    pa_schema_arr = []
    for name in col_names:
        if name not in table_columns:
            pa_schema_arr.append((name, pa.string()))
            continue
        for col in table_columns:
            if str(col) == str(name):
                data_type = (
                    str(table_columns[col]["data_type"])
                    if "data_type" in table_columns[col]
                    else False
                )

                if data_type == "number":
                    pa_schema_arr.append(pa.field(name, pa.float32()))
                elif data_type == "boolean":
                    pa_schema_arr.append(pa.field(name, pa.bool_()))
                else:
                    pa_schema_arr.append(pa.field(name, pa.string()))
    pa_schema = pa.schema(pa_schema_arr)
    return pa_schema


def _create_from_arrays_data(row_data: List) -> List:
    """
    Returns a list that is one array per column. Accepts list that is one
      array per row.
    :param row_data: A list that is made of multiple arrays
    :return: A list of lists.
    """
    if len(row_data) == 0:
        return row_data
    col_data = []
    for row in row_data:
        for i, data in enumerate(row):
            if (len(col_data) - 1) < i:
                col_data.append([])
            col_data[i].append(data)
    return col_data


def _create_parquet_data(data: List[List], pq_schema: pa.Schema) -> List[List]:
    """
    Returns a list with the data being modified to the data types specified by the
      pyarrow schema.
    :param data: A list of lists with multiple objects.
    :param pq_schema: A pyarrow schema file which references the data in the data file.
    :return: A list of lists with data types specified in the pyarrow schema.
    """
    if pq_schema is None:
        for row in data[1:]:
            for i, elm in enumerate(row):
                if elm is None:
                    row[i] = ""
                else:
                    row[i] = str(elm)
        return data
    for row in data[1:]:
        for i, elm in enumerate(row):
            data_type_index = pq_schema.get_field_index(data[0][i])
            data_type = pq_schema.types[data_type_index]
            if data_type == "string":
                if isinstance(elm, str):
                    row[i] = elm
                else:
                    row[i] = str(elm)
            elif data_type == "float":
                if isinstance(elm, float):
                    row[i] = elm
                else:
                    row[i] = float(elm)
            elif data_type == "bool_":
                if isinstance(elm, bool):
                    row[i] = elm
                else:
                    row[i] = bool(elm)
            else:
                row[i] = elm
    return data
