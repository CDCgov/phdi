import csv
import os
import pathlib
import pyarrow as pa
import pyarrow.parquet as pq
import yaml

from pathlib import Path
from typing import Literal, List, Union


def load_schema(path: str) -> dict:
    """
    Given the path to a local YAML file containing a data schema,
    loads the file and return the resulting schema as a dictionary.
    If the file can't be found, raises an error.

    :param path: The file path to a YAML file holding a schema.
    :raises Exception: If the file to be loaded could not be found.
    :return: A dict representing a schema read from the given path.
    """
    try:
        with open(path, "r") as file:
            schema = yaml.safe_load(file)
        return schema
    except FileNotFoundError:
        raise Exception("Could not find path to given file")


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
