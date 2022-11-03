import csv
import os
import yaml
import json
import pathlib
import sqlite3 as sql
from unittest import mock
import pytest

from phdi.tabulation import (
    load_schema,
    write_table,
    print_schema_summary,
)
from phdi.fhir.tabulation import tabulate_data
from phdi.tabulation.tables import write_data


def test_load_schema():
    assert load_schema(
        pathlib.Path(__file__).parent.parent / "assets" / "test_schema.yaml"
    ) == yaml.safe_load(
        open(pathlib.Path(__file__).parent.parent / "assets" / "test_schema.yaml")
    )

    assert load_schema(
        pathlib.Path(__file__).parent.parent / "assets" / "test_schema.json"
    ) == json.load(
        open(pathlib.Path(__file__).parent.parent / "assets" / "test_schema.json")
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


def test_write_data_csv():
    schema = yaml.safe_load(
        open(pathlib.Path(__file__).parent.parent / "assets" / "tabulation_schema.yaml")
    )
    extracted_data = json.load(
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "FHIR_server_extracted_data.json"
        )
    )
    extracted_data = extracted_data.get("entry", {})

    tabulated_data = tabulate_data(extracted_data, schema)
    table_to_use = tabulated_data["Physical Exams"]
    batch_1 = table_to_use[:2]
    batch_2 = [table_to_use[0]] + table_to_use[2:]
    file_location = "./"
    output_file_name = "create_new.csv"
    file_format = "csv"

    if os.path.isfile(file_location + output_file_name):  # pragma: no cover
        os.remove(file_location + output_file_name)

    # Batch 1 tests writing and creating brand new file
    # Only one row actually written in first batch
    write_data(batch_1, file_location, file_format, filename=output_file_name)
    with open(file_location + output_file_name, "r") as csv_file:
        reader = csv.reader(csv_file, dialect="excel")
        line = 0
        for row in reader:
            for i in range(len(row)):
                assert row[i] == str(batch_1[line][i])
            line += 1
        assert line == 2

    # Batch 2 tests appending to existing csv
    # Two more rows written here, make sure no duplicate header row
    write_data(batch_2, file_location, file_format, filename=output_file_name)
    with open(file_location + output_file_name, "r") as csv_file:
        reader = csv.reader(csv_file, dialect="excel")
        line = 0
        for row in reader:
            for i in range(len(row)):
                if row[i] == "":
                    assert table_to_use[line][i] is None
                    continue
                assert row[i] == str(table_to_use[line][i])
            line += 1
        assert line == 4
    os.remove(file_location + output_file_name)


@mock.patch("phdi.tabulation.tables.pq.ParquetWriter")
@mock.patch("phdi.tabulation.tables.pa.Table")
def test_write_data_parquet(patched_pa_table, patched_writer):

    schema = yaml.safe_load(
        open(pathlib.Path(__file__).parent.parent / "assets" / "tabulation_schema.yaml")
    )
    extracted_data = json.load(
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "FHIR_server_extracted_data.json"
        )
    )
    extracted_data = extracted_data.get("entry", {})

    tabulated_data = tabulate_data(extracted_data, schema)
    table_to_use = tabulated_data["Physical Exams"]
    batch_1 = table_to_use[:2]
    batch_2 = [table_to_use[0]] + table_to_use[2:]
    file_location = "./"
    output_file_name = "new_parquet"
    file_format = "parquet"

    # Batch 1 tests creating a new parquet file and returning a writer
    pq_writer = write_data(batch_1, file_location, file_format, output_file_name)
    patched_pa_table.from_arrays.assert_called_with(batch_1[1:], names=batch_1[0])
    table = patched_pa_table.from_arrays(table_to_use[1:], table_to_use[0])
    patched_writer.assert_called_with(file_location + output_file_name, table.schema)
    patched_writer(
        file_location + output_file_name, table.schema
    ).write_table.assert_called_with(table=table)

    # Batch 2 tests appending to existing parquet using previous writer
    write_data(
        batch_2, file_location, file_format, output_file_name, pq_writer=pq_writer
    )
    patched_pa_table.from_arrays.assert_called_with(batch_2[1:], names=batch_2[0])
    table = patched_pa_table.from_arrays(batch_2[1:], batch_2[0])
    pq_writer.write_table.assert_called_with(table=table)

    # One from initial test of creating new pq file, and one
    # from calling it on a mocked table in this test, line 105;
    # Should NOT be called a third time with batch 2
    assert patched_writer.call_count == 2


def test_write_data_sql():
    schema = yaml.safe_load(
        open(pathlib.Path(__file__).parent.parent / "assets" / "tabulation_schema.yaml")
    )
    extracted_data = json.load(
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "FHIR_server_extracted_data.json"
        )
    )
    extracted_data = extracted_data.get("entry", {})

    tabulated_data = tabulate_data(extracted_data, schema)
    table_to_use = tabulated_data["Physical Exams"]
    batch_1 = table_to_use[:2]
    batch_2 = [table_to_use[0]] + table_to_use[2:]
    file_location = "./"
    file_format = "sql"
    db_file = "new_db.db"

    if os.path.isfile(file_location + db_file):  # pragma: no cover
        os.remove(file_location + db_file)

    write_data(
        batch_1, file_location, file_format, db_file=db_file, db_tablename="PATIENT"
    )

    # Check that table was created and row was properly inserted
    conn = sql.connect(file_location + db_file)
    cursor = conn.cursor()
    res = cursor.execute("SELECT name FROM sqlite_master").fetchall()
    assert ("PATIENT",) in res
    res = cursor.execute("SELECT * FROM PATIENT").fetchall()
    assert res == [
        (
            "Price929",
            "Waltham",
            "['obs1']",
            "i-am-not-a-robot",
        )
    ]
    conn.close()

    write_data(
        batch_2, file_location, file_format, db_file=db_file, db_tablename="PATIENT"
    )

    # Check that only new rows were added and data was correctly
    # stored (including empty strings)
    conn = sql.connect(file_location + db_file)
    cursor = conn.cursor()
    res = cursor.execute("SELECT * FROM PATIENT").fetchall()
    assert len(res) == 3
    assert res == [
        (
            "Price929",
            "Waltham",
            "['obs1']",
            "i-am-not-a-robot",
        ),
        ("Shepard", "Zakera Ward", "None", "no-srsly-i-am-hoomun"),
        ("None", "Faketon", "['obs2', 'obs3']", "None"),
    ]
    conn.close()

    os.remove(file_location + db_file)


# @TODO: REMOVE THIS FUNCTION ALONG WITH THE OLD GENERATE ALL TABLES CODE
# ONCE THE NEW TABULATION WORK IS COMPLETE
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


# @TODO: REMOVE THIS FUNCTION ALONG WITH THE OLD GENERATE ALL TABLES CODE
# ONCE THE NEW TABULATION WORK IS COMPLETE
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


# @TODO: REMOVE THIS FUNCTION ALONG WITH THE OLD GENERATE ALL TABLES CODE
# ONCE THE NEW TABULATION WORK IS COMPLETE
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


# @TODO: REMOVE THIS FUNCTION ALONG WITH THE OLD GENERATE ALL TABLES CODE
# ONCE THE NEW TABULATION WORK IS COMPLETE
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
