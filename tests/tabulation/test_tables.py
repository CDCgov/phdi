import copy
import csv
import json
import os
import pathlib
import sqlite3 as sql
from unittest import mock

import jsonschema
import pyarrow as pa
import pyarrow.parquet as pq
import pytest
import yaml

from phdi.fhir.tabulation import tabulate_data
from phdi.tabulation import load_schema
from phdi.tabulation import validate_schema
from phdi.tabulation import write_data
from phdi.tabulation.tables import _convert_list_to_string
from phdi.tabulation.tables import _create_from_arrays_data
from phdi.tabulation.tables import _create_pa_schema_from_table_schema
from phdi.tabulation.tables import _create_parquet_data


def test_load_schema():
    assert load_schema(
        pathlib.Path(__file__).parent.parent
        / "assets"
        / "tabulation"
        / "valid_schema.yaml"
    ) == yaml.safe_load(
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "tabulation"
            / "valid_schema.yaml"
        )
    )

    assert load_schema(
        pathlib.Path(__file__).parent.parent
        / "assets"
        / "tabulation"
        / "valid_schema.json"
    ) == json.load(
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "tabulation"
            / "valid_schema.json"
        )
    )

    # Invalid schema file path
    with pytest.raises(FileNotFoundError):
        load_schema("invalidPath")

    # Invalid JSON
    with pytest.raises(json.decoder.JSONDecodeError):
        load_schema(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "tabulation"
            / "invalid_json.json"
        )

    # Invalid file format
    with pytest.raises(ValueError):
        load_schema(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "tabulation"
            / "sample_hl7.hl7"
        )


def test_write_data_csv():
    schema = yaml.safe_load(
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "tabulation"
            / "tabulation_schema.yaml"
        )
    )
    extracted_data = json.load(
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "general"
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
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "tabulation"
            / "tabulation_schema.yaml"
        )
    )
    extracted_data = json.load(
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "general"
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
    pq_writer = write_data(
        batch_1,
        file_location,
        file_format,
        output_file_name,
        schema=schema,
        table_name="Physical Exams",
    )
    assert pq_writer is not None

    pq_schema = _create_pa_schema_from_table_schema(
        schema, batch_1[0], "Physical Exams"
    )
    patched_pa_table.from_arrays.assert_called_with(
        _create_from_arrays_data(batch_1[1:]), schema=pq_schema
    )
    table = patched_pa_table.from_arrays(table_to_use[1:], table_to_use[0])
    patched_writer.assert_called_with(file_location + output_file_name, table.schema)
    patched_writer(
        file_location + output_file_name, table.schema
    ).write_table.assert_called_with(table=table)

    # Batch 2 tests appending to existing parquet using previous writer
    write_data(
        batch_2,
        file_location,
        file_format,
        output_file_name,
        pq_writer=pq_writer,
        schema=schema,
        table_name="Physical Exams",
    )
    patched_pa_table.from_arrays.assert_called_with(
        _create_from_arrays_data(batch_2[1:]), schema=pq_schema
    )
    table = patched_pa_table.from_arrays(batch_2[1:], batch_2[0])
    pq_writer.write_table.assert_called_with(table=table)

    # One from initial test of creating new pq file, and one
    # from calling it on a mocked table in this test, line 105;
    # Should NOT be called a third time with batch 2
    assert patched_writer.call_count == 2


def test_write_data_parquet_with_schema():
    schema = yaml.safe_load(
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "tabulation"
            / "tabulation_schema.yaml"
        )
    )
    extracted_data = json.load(
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "general"
            / "FHIR_server_extracted_data.json"
        )
    )
    extracted_data = extracted_data.get("entry", {})
    table_name = "Patients"
    table_to_use = tabulate_data(extracted_data, schema, table_name)
    batch_1 = table_to_use[:2]
    batch_2 = [table_to_use[0]] + [table_to_use[2]]
    # Batch 3 has null defined in certain columns, which should be accounted for by the
    #  schema file
    batch_3 = [table_to_use[0]] + table_to_use[3:]
    file_location = "./"
    output_file_name = "new_parquet.parquet"
    file_format = "parquet"

    # Batch 1 tests creating a new parquet file and returning a writer
    pq_writer = write_data(
        batch_1,
        file_location,
        file_format,
        output_file_name,
        None,
        None,
        None,
        schema,
        table_name,
    )
    # Batch 2 tests appending to existing parquet using previous writer
    write_data(
        batch_2,
        file_location,
        file_format,
        output_file_name,
        pq_writer=pq_writer,
        schema=schema,
        table_name=table_name,
    )

    # Batch 3 tests appending to existing parquet using previous writer
    write_data(
        batch_3,
        file_location,
        file_format,
        output_file_name,
        pq_writer=pq_writer,
        schema=schema,
        table_name=table_name,
    )
    pq_writer.close()
    if os.path.isfile(file_location + output_file_name):  # pragma: no cover
        patient_id = pa.array(
            [
                "907844f6-7c99-eabc-f68e-d92189729a55",
                "65489-asdf5-6d8w2-zz5g8",
                "some-uuid",
            ]
        )
        first_name = pa.array(
            [
                "Kimberley248",
                "John",
                "John ",
            ]
        )
        last_name = pa.array(
            [
                "Price929",
                "Shepard",
                "None",
            ]
        )
        phone = pa.array(
            [
                "555-690-3898",
                "None",
                "123-456-7890",
            ]
        )
        bulding_number = pa.array(
            [
                float(165),
                float(1234),
                float(123),
            ]
        )

        names = [
            "Patient ID",
            "First Name",
            "Last Name",
            "Phone Number",
            "Building Number",
        ]
        table_from_arrays = pa.Table.from_arrays(
            [patient_id, first_name, last_name, phone, bulding_number], names=names
        )
        table_parquet_read = pq.read_table(
            file_location + output_file_name, columns=names
        )
        for i, elm in enumerate(table_parquet_read):
            for n, el in enumerate(elm):
                parquet_data = table_parquet_read[i][n]
                array_data = table_from_arrays[i][n]

                # if the number types are the correct type, convert to strings to
                #   compare.
                if isinstance(array_data, pa.DoubleScalar):
                    array_data = str(array_data)
                if isinstance(parquet_data, pa.FloatScalar):
                    parquet_data = str(parquet_data)
                assert parquet_data == array_data

        os.remove(file_location + output_file_name)


def test_write_data_parquet_with_no_schema():
    schema = yaml.safe_load(
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "tabulation"
            / "tabulation_schema.yaml"
        )
    )
    extracted_data = json.load(
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "general"
            / "FHIR_server_extracted_data.json"
        )
    )
    extracted_data = extracted_data.get("entry", {})
    table_name = "Patients"
    table_to_use = tabulate_data(extracted_data, schema, table_name)
    batch_1 = table_to_use[:2]
    batch_2 = [table_to_use[0]] + [table_to_use[2]]
    batch_3 = [table_to_use[0]] + table_to_use[3:]
    file_location = "./"
    output_file_name = "new_parquet.parquet"
    file_format = "parquet"

    # Batch 1 tests creating a new parquet file and returning a writer
    pq_writer = write_data(
        batch_1,
        file_location,
        file_format,
        output_file_name,
        table_name=table_name,
    )
    # Batch 2 tests appending to existing parquet using previous writer
    write_data(
        batch_2,
        file_location,
        file_format,
        output_file_name,
        pq_writer=pq_writer,
        table_name=table_name,
    )

    # Batch 3 tests appending to existing parquet using previous writer
    write_data(
        batch_3,
        file_location,
        file_format,
        output_file_name,
        pq_writer=pq_writer,
        table_name=table_name,
    )
    pq_writer.close()
    if os.path.isfile(file_location + output_file_name):  # pragma: no cover
        patient_id = pa.array(
            [
                "907844f6-7c99-eabc-f68e-d92189729a55",
                "65489-asdf5-6d8w2-zz5g8",
                "some-uuid",
            ]
        )
        first_name = pa.array(
            [
                "Kimberley248",
                "John",
                "John ",
            ]
        )
        last_name = pa.array(
            [
                "Price929",
                "Shepard",
                "",
            ]
        )
        phone = pa.array(
            [
                "555-690-3898",
                "",
                "123-456-7890",
            ]
        )
        bulding_number = pa.array(
            [
                "165",
                "1234",
                "123",
            ]
        )

        names = [
            "Patient ID",
            "First Name",
            "Last Name",
            "Phone Number",
            "Building Number",
        ]
        table_from_arrays = pa.Table.from_arrays(
            [patient_id, first_name, last_name, phone, bulding_number], names=names
        )
        table_parquet_read = pq.read_table(
            file_location + output_file_name, columns=names
        )
        for i, elm in enumerate(table_parquet_read):
            for n, el in enumerate(elm):
                parquet_data = table_parquet_read[i][n]
                array_data = table_from_arrays[i][n]

                # if the number types are the correct type, convert to strings to
                #   compare.
                if isinstance(array_data, pa.DoubleScalar):
                    array_data = str(array_data)
                if isinstance(parquet_data, pa.FloatScalar):
                    parquet_data = str(parquet_data)
                assert parquet_data == array_data

        os.remove(file_location + output_file_name)


def test_write_data_sql():
    schema = yaml.safe_load(
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "tabulation"
            / "tabulation_schema.yaml"
        )
    )
    extracted_data = json.load(
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "general"
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
        ("Shepard", "Boston", "None", "no-srsly-i-am-hoomun"),
        ("None", "Faketon", "obs2,obs3", "None"),
    ]
    conn.close()

    os.remove(file_location + db_file)


def test_validate_schema():
    valid_schema = yaml.safe_load(
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "tabulation"
            / "valid_schema.yaml"
        )
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


def test_create_pa_schema_from_table_schema():
    schema = yaml.safe_load(
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "tabulation"
            / "tabulation_schema.yaml"
        )
    )
    extracted_data = json.load(
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "general"
            / "FHIR_server_extracted_data.json"
        )
    )
    extracted_data = extracted_data.get("entry", {})

    table_to_use = tabulate_data(extracted_data, schema, "Patients")
    names = table_to_use[0] + ["test"]
    schema["tables"]["Patients"]["columns"]["Last Name"]["data_type"] = "boolean"
    pq_schema = _create_pa_schema_from_table_schema(schema, names, "Patients")
    assert pq_schema == pa.schema(
        [
            ("Patient ID", pa.string()),
            ("First Name", pa.string()),
            ("Last Name", pa.bool_()),
            ("Phone Number", pa.string()),
            ("Building Number", pa.float32()),
            ("test", pa.string()),
        ]
    )


def test_create_from_arrays_data():
    result = _create_from_arrays_data([["foo", "bar", "baz"], ["biz", "taz", "laz"]])
    assert result == [["foo", "biz"], ["bar", "taz"], ["baz", "laz"]]


def test_create_parquet_data():
    schema = yaml.safe_load(
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "tabulation"
            / "tabulation_schema.yaml"
        )
    )
    extracted_data = json.load(
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "general"
            / "FHIR_server_extracted_data.json"
        )
    )
    extracted_data = extracted_data.get("entry", {})
    table_to_use = tabulate_data(extracted_data, schema, "Patients")
    batch_1 = [table_to_use[0]] + table_to_use[3:]

    pq_schema = _create_pa_schema_from_table_schema(schema, table_to_use[0], "Patients")
    result = _create_parquet_data(batch_1, pq_schema)
    assert result == [
        ["Patient ID", "First Name", "Last Name", "Phone Number", "Building Number"],
        ["some-uuid", "John ", "None", "123-456-7890", 123.0],
    ]
