import os
from phdi.cloud.azure import AzureCloudContainerConnection, AzureCredentialManager
from phdi.cloud.gcp import GcpCloudStorageConnection, GcpCredentialManager
import pytest
from app.utils import (
    check_for_fhir,
    check_for_fhir_bundle,
    search_for_required_values,
    get_credential_manager,
    get_cloud_provider_storage_connection,
)
from app.config import get_settings


def test_search_for_required_values_success():
    input = {"salt_str": "request-value"}
    required_values = ["credential_manager"]
    os.environ["CREDENTIAL_MANAGER"] = "azure"
    os.environ["SALT_STR"] = "environment-value"

    get_settings.cache_clear()
    message = search_for_required_values(input, required_values)

    assert input == {"salt_str": "request-value", "credential_manager": "azure"}
    assert message == "All values were found."


def test_search_for_required_values_failure():
    input = {"salt_str": "request-value"}
    required_values = ["credential_manager"]
    os.environ.pop("CREDENTIAL_MANAGER", None)
    os.environ["SALT_STR"] = "environment-value"

    get_settings.cache_clear()
    message = search_for_required_values(input, required_values)

    assert input == {"salt_str": "request-value"}
    assert message == (
        "The following values are required, but were not included in the request and "
        "could not be read from the environment. Please resubmit the request including "
        "these values or add them as environment variables to this service. missing "
        "values: credential_manager."
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


def test_get_credential_manager_azure():
    expected_result = AzureCredentialManager
    actual_result = get_credential_manager("azure")
    assert actual_result == expected_result


def test_get_credential_manager_gcp():
    expected_result = GcpCredentialManager
    actual_result = get_credential_manager("gcp")
    assert actual_result == expected_result


def test_get_credential_manager_invalid():
    expected_result = None
    actual_result = get_credential_manager("myown")
    assert actual_result == expected_result


def test_get_cloud_provider_azure():
    expected_result = AzureCloudContainerConnection
    actual_result = get_cloud_provider_storage_connection("azure")
    assert actual_result == expected_result


def test_get_cloud_provider_gcp():
    expected_result = GcpCloudStorageConnection
    actual_result = get_cloud_provider_storage_connection("gcp")
    assert actual_result == expected_result


def test_get_cloud_provider_invalid():
    expected_result = None
    actual_result = get_cloud_provider_storage_connection("myown")
    assert actual_result == expected_result
