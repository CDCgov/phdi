import json
import os
from pathlib import Path
from unittest import mock

import pytest
from app.config import get_settings
from app.utils import convert_to_fhir
from app.utils import field_metadata
from app.utils import freeze_parsing_schema
from app.utils import freeze_parsing_schema_helper
from app.utils import get_credential_manager
from app.utils import get_metadata
from app.utils import get_parsers
from app.utils import load_parsing_schema
from app.utils import search_for_required_values
from frozendict import frozendict


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


@mock.patch("app.utils.fhirpathpy")
def test_get_parsers(patched_fhirpathpy):
    parsing_schema = load_parsing_schema("test_reference_schema.json")
    get_parsers.cache_clear()
    get_parsers(frozendict(parsing_schema))

    expected_number_of_calls = 0
    for field, field_definition in parsing_schema.items():
        expected_number_of_calls += 1
        if "secondary_schema" in field_definition:
            expected_number_of_calls += len(field_definition["secondary_schema"])

    assert len(patched_fhirpathpy.compile.call_args_list) == expected_number_of_calls


def test_search_for_required_values_success():
    input = {"salt_str": "request-value"}
    required_values = ["fhir_converter_url"]
    os.environ["FHIR_CONVERTER_URL"] = "my-fhir-converter-url"
    os.environ["SALT_STR"] = "environment-value"

    get_settings.cache_clear()
    message = search_for_required_values(input, required_values)

    os.environ.pop("CRED_MANAGER", None)
    os.environ.pop("SALT_STR", None)
    assert input == {
        "salt_str": "request-value",
        "fhir_converter_url": "my-fhir-converter-url",
    }
    assert message == "All values were found."


def test_search_for_required_values_failure():
    input = {"salt_str": "request-value"}
    required_values = ["cred_manager"]
    os.environ.pop("CRED_MANAGER", None)
    os.environ["SALT_STR"] = "environment-value"

    get_settings.cache_clear()
    message = search_for_required_values(input, required_values)
    os.environ.pop("CRED_MANAGER", None)
    os.environ.pop("SALT_STR", None)

    assert input == {"salt_str": "request-value"}
    assert message == (
        "The following values are required, but were not included in the request and "
        "could not be read from the environment. Please resubmit the request including "
        "these values or add them as environment variables to this service. missing "
        "values: cred_manager."
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


@mock.patch("app.utils.http_request_with_reauth")
def test_convert_fhir_cred_manager(patched_requests_with_reauth):
    credential_manager = mock.Mock()
    credential_manager.get_access_token.return_value = "some-access-token"
    parameters = {
        "message": "some message to convert",
        "message_type": "elr",
        "fhir_converter_url": "some FHIR converter URL",
        "headers": {},
        "credential_manager": credential_manager,
    }
    convert_to_fhir(**parameters)
    patched_requests_with_reauth.assert_called_with(
        credential_manager=credential_manager,
        url="some FHIR converter URL/convert-to-fhir",
        retry_count=3,
        request_type="POST",
        allowed_methods=["POST"],
        headers={"Authorization": "Bearer some-access-token"},
        data={
            "input_data": "some message to convert",
            "input_type": "hl7v2",
            "root_template": "ORU_R01",
        },
    )


@mock.patch("app.utils.http_request_with_retry")
def test_convert_fhir_no_cred_manager(patched_requests_with_retryh):
    parameters = {
        "message": "some message to convert",
        "message_type": "elr",
        "fhir_converter_url": "some FHIR converter URL",
        "headers": {},
    }
    convert_to_fhir(**parameters)
    patched_requests_with_retryh.assert_called_with(
        url="some FHIR converter URL/convert-to-fhir",
        retry_count=3,
        request_type="POST",
        allowed_methods=["POST"],
        headers={},
        data={
            "input_data": "some message to convert",
            "input_type": "hl7v2",
            "root_template": "ORU_R01",
        },
    )


def test_freeze_parsing_schema():
    test_schema_path = (
        Path(__file__).parent.parent / "app" / "default_schemas" / "test_schema.json"
    )
    with open(test_schema_path, "r") as file:
        test_schema = json.load(file)

    frozen_schema = freeze_parsing_schema(test_schema)

    for key in test_schema:
        for subkey in test_schema[key]:
            assert test_schema[key][subkey] == frozen_schema[key][subkey]


def test_field_metadata():
    expected_result = {
        "value": "foo",
        "fhir_path": "bar",
        "data_type": "biz",
        "resource_type": "baz",
    }
    assert (
        field_metadata(
            value="foo", fhir_path="bar", data_type="biz", resource_type="baz"
        )
        == expected_result
    )
    expected_result2 = {
        "value": "",
        "fhir_path": "",
        "data_type": "",
        "resource_type": "",
    }
    assert field_metadata() == expected_result2


def test_get_metadata():
    example_parsed_values = {"foo": "bar", "fiz": "biz", "baz": "Null"}
    example_schema = {
        "foo": {
            "fhir_path": "Bundle.entry.resource.where(resourceType='Foo').biz",
            "data_type": "string",
            "nullable": False,
            "metadata": {"metaFoo": "metaFooData", "metaFiz": "metaFizData"},
        },
        "baz": {},
    }
    expected_result = {
        "foo": {
            "value": "bar",
            "fhir_path": "Bundle.entry.resource.where(resourceType='Foo').biz",
            "data_type": "string",
            "resource_type": "Foo",
            "metaFoo": "metaFooData",
            "metaFiz": "metaFizData",
        },
        "fiz": {"value": "biz", "fhir_path": "", "data_type": "", "resource_type": ""},
        "baz": {"value": "Null", "fhir_path": "", "data_type": "", "resource_type": ""},
    }
    result = get_metadata(parsed_values=example_parsed_values, schema=example_schema)
    assert result == expected_result


def test_freeze_parsing_schema_helper():
    input = {"foo": "bar", "fiz": {"foo": "bar", "fiz": {"foo": "bar"}}}
    output = freeze_parsing_schema_helper(input)
    assert isinstance(output, frozendict)
    assert isinstance(output["fiz"], frozendict)
    assert isinstance(output["fiz"]["fiz"], frozendict)
    assert isinstance(output["foo"], str)
