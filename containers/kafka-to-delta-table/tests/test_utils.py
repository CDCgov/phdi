import json
from pathlib import Path
from app.utils import get_spark_schema, validate_schema, load_schema
from pyspark.sql.types import StructType, StructField, StringType
import pytest


def test_get_spark_schema():
    schema_config = {"first_name": "string", "last_name": "string"}
    schema_config = json.dumps(schema_config)
    expected_schema = StructType()
    expected_schema.add(StructField("first_name", StringType(), True))
    expected_schema.add(StructField("last_name", StringType(), True))

    assert get_spark_schema(schema_config) == expected_schema


def test_validate_schema():
    good_json_schema = {"first_name": "string", "last_name": "string"}
    assert validate_schema(good_json_schema) == {"valid": True, "errors": []}

    bad_json_schema = {"first_name": "string", 1: "some-invalid-type"}
    assert validate_schema(bad_json_schema) == {
        "valid": False,
        "errors": [
            "Invalid field name: 1. Field names must be strings.",
            "Invalid type for field 1: some-invalid-type. Valid types are "
            "['string', 'integer', 'float', 'boolean', 'date', 'timestamp'].",
        ],
    }

def test_load_parsing_schema_success():
    test_schema_path = (
        Path(__file__).parent.parent / "app" / "default_schemas" / "test_schema.json"
    )
    with open(test_schema_path, "r") as file:
        test_schema = json.load(file)

    schema = load_schema("test_schema.json")
    assert schema == test_schema


def test_load_parsing_schema_fail():
    bad_schema_name = "schema-that-does-not-exist.json"
    with pytest.raises(FileNotFoundError) as error:
        load_schema(bad_schema_name)
    assert error.value.args == (
        f"A schema with the name '{bad_schema_name}' could not be found.",
    )