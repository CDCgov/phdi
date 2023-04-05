import json
from app.utils import get_spark_schema
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType
)


def test_get_spark_schema():
    
    schema_config = {"first_name": "string", "last_name": "string"}
    schema_config = json.dumps(schema_config)
    expected_schema = StructType()
    expected_schema.add(StructField("first_name", StringType(), True))
    expected_schema.add(StructField("last_name", StringType(), True))
    
    assert get_spark_schema(schema_config) == expected_schema