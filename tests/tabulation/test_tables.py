import csv
import os
import jsonschema
import yaml
import json
import pathlib
import pytest
from unittest import mock
import copy

from phdi.tabulation import (
    load_schema,
    write_table,
    print_schema_summary,
    validate_schema,
)


def test_load_schema():
    assert load_schema(
        pathlib.Path(__file__).parent.parent / "assets" / "valid_schema.yaml"
    ) == yaml.safe_load(
        open(pathlib.Path(__file__).parent.parent / "assets" / "valid_schema.yaml")
    )

    assert load_schema(
        pathlib.Path(__file__).parent.parent / "assets" / "valid_schema.json"
    ) == json.load(
        open(pathlib.Path(__file__).parent.parent / "assets" / "valid_schema.json")
    )

    # Invalid schema file path
    with pytest.raises(FileNotFoundError):
        load_schema("invalidPath")

    # Invalid JSON
    with pytest.raises(json.decoder.JSONDecodeError):
        load_schema(
            pathlib.Path(__file__).parent.parent / "assets" / "invalid_json.json"
        )

    # Invalid file format
    with pytest.raises(ValueError):
        load_schema(pathlib.Path(__file__).parent.parent / "assets" / "sample_hl7.hl7")


def test_validate_schema():

    valid_schema = yaml.safe_load(
        open(pathlib.Path(__file__).parent.parent / "assets" / "valid_schema.yaml")
    )

    assert validate_schema(schema=valid_schema) is None

    # Invalid data type
    invalid_data_type = copy.deepcopy(valid_schema)
    invalid_data_type["tables"]["table 1A"]["resource_type"] = 10

    with pytest.raises(jsonschema.exceptions.ValidationError) as e:
        validate_schema(schema=invalid_data_type)
    assert "10 is not of type 'string'" in str(e.value)

    # Required element is not present
    missing_fhir_path = copy.deepcopy(valid_schema)
    del missing_fhir_path["tables"]["table 1A"]["columns"]["Patient ID"]["fhir_path"]
    with pytest.raises(jsonschema.exceptions.ValidationError) as e:
        validate_schema(schema=missing_fhir_path)
    assert "'fhir_path' is a required property" in str(e.value)

    # Invalid selection_criteria
    bad_selection_criteria = copy.deepcopy(valid_schema)
    bad_selection_criteria["tables"]["table 1A"]["columns"]["Patient ID"][
        "selection_criteria"
    ] = "test"
    with pytest.raises(jsonschema.exceptions.ValidationError) as e:
        validate_schema(schema=bad_selection_criteria)
    assert "'test' is not one of ['first', 'last', 'random']" in str(e.value)


@mock.patch("phdi.tabulation.tables.pq.ParquetWriter")
@mock.patch("phdi.tabulation.tables.pa.Table")
def test_write_schema_table_no_writer(patched_pa_table, patched_writer):

    data = [{"some_column": "some value", "some_other_column": "some other value"}]
    output_file_name = mock.Mock()
    file_format = "parquet"

    write_table(data, output_file_name, file_format)
    patched_pa_table.from_pylist.assert_called_with(data)
    table = patched_pa_table.from_pylist(data)

    patched_writer.assert_called_with(output_file_name, table.schema)
    patched_writer(output_file_name, table.schema).write_table.assert_called_with(
        table=table
    )


@mock.patch("phdi.tabulation.tables.pq.ParquetWriter")
@mock.patch("phdi.tabulation.tables.pa.Table")
def test_write_schema_table_with_writer(patched_pa_table, patched_writer):

    data = [{"some_column": "some value", "some_other_column": "some other value"}]
    output_file_name = mock.Mock()
    file_format = "parquet"
    writer = mock.Mock()

    write_table(data, output_file_name, file_format, writer)
    patched_pa_table.from_pylist.assert_called_with(data)
    table = patched_pa_table.from_pylist(data)
    writer.write_table.assert_called_with(table=table)
    assert len(patched_writer.call_args_list) == 0


def test_write_schema_table_new_csv():
    data = [{"some_column": "some value", "some_other_column": "some other value"}]
    output_file_name = "create_new.csv"
    file_format = "csv"

    if os.path.isfile(output_file_name):  # pragma: no cover
        os.remove(output_file_name)

    write_table(data, output_file_name, file_format)

    with open(output_file_name, "r") as csv_file:
        reader = csv.reader(csv_file, dialect="excel")
        assert next(reader) == list(data[0].keys())

    os.remove(output_file_name)


def test_write_schema_table_append_csv():
    data = [{"some_column": "some value", "some_other_column": "some other value"}]
    output_file_name = "append.csv"
    file_format = "csv"

    if os.path.isfile(output_file_name):  # pragma: no cover
        os.remove(output_file_name)

    # do it thrice to append
    write_table(data, output_file_name, file_format)
    write_table(data, output_file_name, file_format)
    write_table(data, output_file_name, file_format)

    with open(output_file_name, "r") as csv_file:
        reader = csv.reader(csv_file, dialect="excel")
        assert next(reader) == list(data[0].keys())
        assert len(csv_file.readlines()) == 3
    os.remove(output_file_name)


@mock.patch("phdi.tabulation.tables.pq.read_table")
@mock.patch("phdi.tabulation.tables.pq.ParquetFile")
@mock.patch("phdi.tabulation.tables.os.walk")
def test_print_schema_summary_parquet(
    patched_os_walk, patched_ParquetFile, patched_reader
):

    patched_os_walk.return_value = [("some_path", None, ["filename.parquet"])]

    schema_directory = mock.Mock()
    display_head = False
    print_schema_summary(schema_directory, display_head)
    patched_ParquetFile.assert_called_with(
        pathlib.Path("some_path") / "filename.parquet"
    )
    assert len(patched_reader.call_args_list) == 0

    display_head = True
    print_schema_summary(schema_directory, display_head)
    patched_ParquetFile.assert_called_with(
        pathlib.Path("some_path") / "filename.parquet"
    )
    patched_reader.assert_called_with(pathlib.Path("some_path") / "filename.parquet")


@mock.patch("phdi.tabulation.tables.os.walk")
def test_print_schema_summary_csv(patched_os_walk, capsys):
    data = [{"some_column": "some value", "some_other_column": "some other value"}]
    output_file_name = "print_schema.csv"
    file_format = "csv"

    patched_os_walk.return_value = [("", None, ["print_schema.csv"])]
    schema_directory = mock.Mock()

    if os.path.isfile(output_file_name):  # pragma: no cover
        os.remove(output_file_name)

    write_table(data, output_file_name, file_format)

    print_schema_summary(schema_directory)
    captured = capsys.readouterr()
    # the \n is because print in python automatically adds \n
    assert captured.out == "['some_column', 'some_other_column']\n"

    os.remove(output_file_name)
