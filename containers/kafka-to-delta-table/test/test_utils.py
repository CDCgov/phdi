import json
from app.utils import get_spark_schema, validate_schema
from pyspark.sql.types import StructType, StructField, StringType


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
