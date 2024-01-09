import os

import pytest
from app.config import get_settings
from app.utils import check_for_fhir
from app.utils import check_for_fhir_bundle
from app.utils import get_cloud_provider_storage_connection
from app.utils import get_cred_manager
from app.utils import search_for_required_values


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


def test_check_for_fhir():
    good_fhir = {"resourceType": "Patient"}
    assert check_for_fhir(good_fhir) == good_fhir

    bad_fhir = {}
    with pytest.raises(AssertionError):
        check_for_fhir(bad_fhir)


def test_check_for_fhir_bundle():
    good_fhir = {"resourceType": "Bundle"}
    assert check_for_fhir_bundle(good_fhir) == good_fhir

    bad_fhir = {"resourceType": "Patient"}
    with pytest.raises(AssertionError):
        check_for_fhir_bundle(bad_fhir)


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


def test_get_cloud_provider_azure():
    storage_url = "Storage URL"

    actual_result = get_cloud_provider_storage_connection("azure", storage_url)
    assert hasattr(actual_result, "__class__")
    assert hasattr(actual_result, "storage_account_url")


def test_get_cloud_provider_gcp():
    actual_result = get_cloud_provider_storage_connection("gcp")
    assert hasattr(actual_result, "__class__")
    assert hasattr(actual_result, "_get_storage_client")


def test_get_cloud_provider_invalid():
    expected_result = None
    actual_result = get_cloud_provider_storage_connection("myown")
    assert actual_result == expected_result
