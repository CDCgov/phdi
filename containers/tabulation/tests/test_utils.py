import os
import pytest
import pathlib
import json
from app.utils import (
    search_for_required_values,
    get_cred_manager,
    check_schema_validity,
)
from app.config import get_settings


def test_search_for_required_values_success():
    input = {"salt_str": "request-value"}
    required_values = ["cred_manager"]
    os.environ["CRED_MANAGER"] = "azure"
    os.environ["SALT_STR"] = "environment-value"

    get_settings.cache_clear()
    message = search_for_required_values(input, required_values)

    os.environ.pop("CRED_MANAGER", None)
    os.environ.pop("SALT_STR", None)

    assert input == {"salt_str": "request-value", "cred_manager": "azure"}
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


def test_get_cred_manager_azure():
    fhir_url = "Some URL"
    actual_result = get_cred_manager("azure", fhir_url)
    assert hasattr(actual_result, "__class__")
    assert hasattr(actual_result, "resource_location")
    assert hasattr(actual_result, "access_token")


def test_get_cred_manager_gcp():
    actual_result = get_cred_manager("gcp")
    assert hasattr(actual_result, "__class__")
    assert hasattr(actual_result, "scoped_credentials")


def test_get_cred_manager_invalid():
    expected_result = None
    actual_result = get_cred_manager("myown")
    assert actual_result == expected_result


def test_check_schema_validity_invalid_schema():
    invalid_schema = {}
    with pytest.raises(AssertionError):
        check_schema_validity(invalid_schema)


def test_check_schema_validity_valid_schema():
    valid_schema_path = (
        pathlib.Path(__file__).parent.parent.parent.parent
        / "tests"
        / "assets"
        / "valid_schema.json"
    )
    valid_schema = json.load(open(valid_schema_path))

    try:
        check_schema_validity(valid_schema)
    except AssertionError:
        pytest.fail("A valid schema raised an exception which should not happen.")
