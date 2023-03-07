import json
from pathlib import Path
import pytest
from app.utils import load_parsing_schema


def test_load_parsing_schema_success():
    test_schema_path = (
        Path(__file__).parent.parent / "app" / "default_schemas" / "test_schema.json"
    )
    with open(test_schema_path, "r") as file:
        test_schema = json.load(file)

    schema = load_parsing_schema("test_schema.json")
    assert schema == test_schema


def test_load_parsing_schema_fail():
    bad_schema_name = "schema-that-does-not-exist.json"
    with pytest.raises(FileNotFoundError) as error:
        load_parsing_schema(bad_schema_name)
    assert error.value.args == (
        f"A schema with the name '{bad_schema_name}' could not be found.",
    )
