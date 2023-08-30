import json
from pathlib import Path
import pytest
from app.utils import (
    load_processing_schema,
    get_credential_manager,
    freeze_processing_schema,
)


def test_load_processing_schema_success():
    test_schema_path = (
        Path(__file__).parent.parent / "app" / "default_schemas" / "test_schema.json"
    )
    with open(test_schema_path, "r") as file:
        test_schema = json.load(file)

    schema = load_processing_schema("test_schema.json")
    assert schema == test_schema


def test_load_processing_schema_fail():
    bad_schema_name = "schema-that-does-not-exist.json"
    with pytest.raises(FileNotFoundError) as error:
        load_processing_schema(bad_schema_name)
    assert error.value.args == (
        f"A schema with the name '{bad_schema_name}' could not be found.",
    )


def test_get_credential_manager_azure():
    fhir_url = "Some URL"
    actual_result = get_credential_manager("azure", fhir_url)
    assert hasattr(actual_result, "__class__")
    assert hasattr(actual_result, "resource_location")
    assert hasattr(actual_result, "access_token")


def test_get_credential_manager_gcp():
    actual_result = get_credential_manager("gcp")
    assert hasattr(actual_result, "__class__")
    assert hasattr(actual_result, "scoped_credentials")


def test_get_credential_manager_invalid():
    expected_result = None
    actual_result = get_credential_manager("myown")
    assert actual_result == expected_result


def test_freeze_processing_schema():
    test_schema_path = (
        Path(__file__).parent.parent / "app" / "default_schemas" / "test_schema.json"
    )
    with open(test_schema_path, "r") as file:
        test_schema = json.load(file)

    frozen_schema = freeze_processing_schema(test_schema)

    for key in test_schema:
        for subkey in test_schema[key]:
            assert test_schema[key][subkey] == frozen_schema[key][subkey]
