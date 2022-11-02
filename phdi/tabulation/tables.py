import csv
import os
import pathlib
import yaml
import json
import pyarrow as pa
import pyarrow.parquet as pq
import sqlite3 as sql
import yaml

from pathlib import Path
from typing import Literal, List, Union


def load_schema(path: pathlib.Path) -> dict:
    """
    Given the path to a local YAML file containing a data schema,
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
        return schema
    except FileNotFoundError:
        raise FileNotFoundError(
            "The specified file does not exist at the path provided."
        )
    except json.decoder.JSONDecodeError as e:
        raise json.decoder.JSONDecodeError(
            "The specified file is not valid JSON.", e.doc, e.pos
        )


def write_data(
    tabulated_data: List[List],
    location: str,
    output_type: Literal["csv", "parquet", "sql"],
    filename: str = None,
    db_file: str = None,
    db_tablename: str = None,
    pq_writer: pq.ParquetWriter = None,
) -> Union[None, pq.ParquetWriter]:
    """
    Writes a set of tabulated data to a particular output format on disk.
    The given data should be tabulated using the `tabulate_data` function
    in fhir/tabulation. This function can write output to a variety of
    formats, including CSV, Parquet, or SQL. In the case of the first
    two formats, a filename must be provided to write output to. In the
    case of the third format, a database file (if one exists) should be
    specified along with a table name. Creates new data files if the
    given options specify a file that doesn't exist, and appends data
    to already-present files if they do.

    :param tabulated_data: The output of the `tabulate_data` function, a
      list of lists in which the first element is the headers for the
      table-to-write and subsequent elements are rows in the table.
    :param location: The directory in which to write the output data
      (if `output_type` is CSV or Parquet), or the directory in which
      the `db_file` is stored (if a database already exists) or should
      be created in (if a database does not already exist).
    :param output_type: The format the data should be written to.
    :param filename: The name of the CSV or Parquet file data should be
      written to. Can be omitted if `output_type` is SQL. Default: `None`.
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
    if output_type == "csv":
        write_headers = False if os.path.isfile(location + filename) else True
        with open(location + filename, "a", newline="") as fp:
            writer = csv.writer(fp)
            if write_headers:
                writer.writerow(tabulated_data[0])
            writer.writerows(tabulated_data[1:])

    if output_type == "parquet":
        table = pa.Table.from_arrays(tabulated_data[1:], names=tabulated_data[0])
        if pq_writer is None:
            pq_writer = pq.ParquetWriter(location + filename, table.schema)
        pq_writer.write_table(table=table)
        return pq_writer

    if output_type == "sql":

        # We need a file-space cursor to operate on a connected table
        conn = sql.connect(location + db_file)
        cursor = conn.cursor()

        # Create requested table if it's not already in the database
        headers = tuple(tabulated_data[0])
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {db_tablename} {headers};")

        # Format the programmatic values correctly by number of cols
        # Need this ugly construction so that the binding placeholder qmarks
        # don't have quotes around them individually when parsed by the SQL
        # engine
        hdr_placeholder = "({})".format(", ".join("?" * len(tabulated_data[0])))
        tuple_data = [tuple(row) for row in tabulated_data[1:]]
        # Have to do a format string this way to avoid an empty f-string error
        cursor.executemany(
            "INSERT INTO {} {} VALUES {};".format(
                db_tablename, headers, hdr_placeholder
            ),
            tuple_data,
        )

        conn.commit()
        conn.close()


# @TODO: REMOVE THIS FUNCTION ALONG WITH THE OLD GENERATE ALL TABLES CODE
# ONCE THE NEW TABULATION WORK IS COMPLETE
def write_table(
    data: List[dict],
    output_file_name: pathlib.Path,
    file_format: Literal["parquet", "csv"],
    writer: pq.ParquetWriter = None,
) -> Union[None, pq.ParquetWriter]:
    """
    Given data stored as a list of dictionaries, where all dictionaries
    have a common set of keys, writes the set of data to an output
    file of a particular type.

    :param data: A list of dictionaries representing the table's data.
      Each dictionary represents one row in the resulting table. The
      keys serve as the table's columns, and the values represent the
      entry for that column in the row given by a particular dict.
    :param output_file_name: The full name for the file where the table
      is to be written.
    :param output_format: The file format of the table to be written.
    :param writer: A writer object that can be maintained
      between different calls of this function to support file formats
      that cannot be appended to after being written (e.g. parquet). Default: `None`
    :return: An instance of `pq.ParquetWriter` if file_format is parquet,
      otherwise `None`
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
    directory: pathlib.Path,
    display_head: bool = False,
) -> None:
    """
    Prints a summary of each CSV of Parquet formatted table in a given directory of
    tables.

    :param directory: The path to a direct holding table files.
    :param display_head: If true, print the first few rows of each table;
      if false, only print table metadata. Default: `False`

      Note: depending on the file format, this may require
      reading large amounts of data into memory.
    """
    for (directory_path, _, file_names) in os.walk(directory):
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
