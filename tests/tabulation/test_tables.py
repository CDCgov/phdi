import csv
import os
import jsonschema
import yaml
import json
import pathlib
import sqlite3 as sql
from unittest import mock
import pytest
import copy

from phdi.tabulation import (
    load_schema,
    validate_schema,
    write_data,
)
from phdi.fhir.tabulation import tabulate_data
from phdi.tabulation.tables import (
    _convert_list_to_string,
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

    table_to_use = tabulate_data(extracted_data, schema, "Physical Exams")
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

    table_to_use = tabulate_data(extracted_data, schema, "Physical Exams")
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

    table_to_use = tabulate_data(extracted_data, schema, "Physical Exams")
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
            "obs1",
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
            "obs1",
            "i-am-not-a-robot",
        ),
        ("Shepard", "Zakera Ward", "None", "no-srsly-i-am-hoomun"),
        ("None", "Faketon", "obs2,obs3", "None"),
    ]
    conn.close()

    os.remove(file_location + db_file)


def test_validate_schema():
    valid_schema = yaml.safe_load(
        open(pathlib.Path(__file__).parent.parent / "assets" / "valid_schema.yaml")
    )
    first_name = valid_schema["tables"]["table 1A"]["columns"]["First Name"]
    patient_id = valid_schema["tables"]["table 1A"]["columns"]["Patient ID"]

    # data_type is defined on first_name, and not on patient_id
    assert "data_type" in first_name.keys()
    assert "data_type" not in patient_id.keys()

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
    assert "'test' is not one of ['first', 'last', 'random', 'all']" in str(e.value)

    # Invalid data type declaration
    invalid_data_type_declaraction = copy.deepcopy(valid_schema)
    invalid_data_type_declaraction["tables"]["table 1A"]["columns"]["First Name"][
        "data_type"
    ] = "foo"

    with pytest.raises(jsonschema.exceptions.ValidationError) as e:
        validate_schema(schema=invalid_data_type_declaraction)
    assert "'foo' is not one of ['string', 'number', 'boolean']" in str(e.value)

    # Missing schema_name
    missing_schema = copy.deepcopy(valid_schema)
    del missing_schema["metadata"]["schema_name"]
    with pytest.raises(jsonschema.exceptions.ValidationError) as e:
        validate_schema(schema=missing_schema)
    assert "'schema_name' is a required property" in str(e.value)


def test_convert_list_to_string():
    array_source = [
        "string",
        ["array-string-1", "array-string-2"],
        [["array-array-1-1", "array-array-1-2"], 2],
        {"foo": "bar"},
    ]
    array_result = (
        "string,array-string-1,array-string-2,array-array-1-1"
        + ",array-array-1-2,2,{'foo': 'bar'}"
    )
    assert _convert_list_to_string(array_source) == array_result
