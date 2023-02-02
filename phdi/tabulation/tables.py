import csv
import os
import pathlib
import json
import pyarrow as pa
import pyarrow.parquet as pq
import sqlite3 as sql
import yaml

from typing import Literal, List, Union
from jsonschema import validate
import importlib.resources


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
        table = pa.Table.from_arrays(tabulated_data[1:], names=tabulated_data[0])
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
    """
    for i, v in enumerate(val):
        if isinstance(v, list):
            val[i] = _convert_list_to_string(v)
        elif isinstance(v, dict):
            val[i] = str(v)
        elif type(v) != str:
            val[i] = str(v)
    return (",").join(val)
