from typing import Any
from app.config import get_settings
from phdi.cloud.azure import AzureCloudContainerConnection, AzureCredentialManager
from phdi.cloud.gcp import GcpCloudStorageConnection, GcpCredentialManager


cloud_providers = {
    "azure": AzureCloudContainerConnection,
    "gcp": GcpCloudStorageConnection,
}
cred_managers = {"azure": AzureCredentialManager, "gcp": GcpCredentialManager}


def check_for_fhir(value: dict) -> dict:
    """
    Check if the value provided is a valid FHIR resource or bundle by asserting that
    a 'resourceType' key exists with a non-null value.

    :param value: Dictionary to be tested for FHIR validity.
    :return: The dictionary originally passed in as 'value'
    """

    assert value.get("resourceType") not in [
        None,
        "",
    ], "Must provide a FHIR resource or bundle"
    return value


def check_for_fhir_bundle(value: dict) -> dict:
    """
    Check if the dictionary provided is a valid FHIR bundle by asserting that a
    'resourceType' key exists with the value 'Bundle'.

    :param value: Dictionary to be tested for FHIR validity.
    :return: The dictionary originally passed in as 'value'
    """

    assert (
        value.get("resourceType") == "Bundle"
    ), "Must provide a FHIR resource or bundle"  # noqa
    return value


def search_for_required_values(input: dict, required_values: list) -> str:
    """
    Search for required values in the input dictionary and the environment.
    Found in the environment not present in the input dictionary that are found in the
    environment are added to the dictionary. A message is returned indicating which,
    if any, required values could not be found.

    :param input: A dictionary potentially originating from the body of a POST request
    :param required_values: A list of values to search for in the input dictionary and
    the environment.
    :return: A string message indicating if any required values could not be found and
    if so which ones.
    """

    missing_values = []

    for value in required_values:
        if input.get(value) in [None, ""]:
            if get_settings().get(value) is None:
                missing_values.append(value)
            else:
                input[value] = get_settings()[value]

    message = "All values were found."
    if missing_values != []:
        message = (
            "The following values are required, but were not included in the request "
            "and could not be read from the environment. Please resubmit the request "
            "including these values or add them as environment variables to this "
            f"service. missing values: {', '.join(missing_values)}."
        )

    return message


def get_cred_manager(cred_manager: str) -> Any:
    """
    Return a credential manager for different cloud providers depending upon which
    one the user requests via the parameter.

    :param credential_manager: A string identifying which cloud credential
    manager is desired.
    :return: Either a Google Cloud Credential Manager or an Azure Credential Manager
    depending upon the value passed in.
    """
    result = cred_managers.get(cred_manager)
    return result


def get_cloud_provider_storage_connection(cloud_provider: str) -> Any:
    """
    Return a cloud provider storage connection for different cloud providers
    depending upon which one the user requests via the parameter.

    :param cloud_provider: A string identifying which cloud provider is desired.
    :return: Either a Google Cloud Storage Connection or an Azure Storage
    Connection depending upon the value passed in.
    """
    result = cloud_providers.get(cloud_provider)
    return result
