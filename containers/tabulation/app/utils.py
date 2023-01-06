from app.config import get_settings
from phdi.cloud.azure import AzureCloudContainerConnection, AzureCredentialManager
from phdi.cloud.core import BaseCredentialManager
from phdi.cloud.gcp import GcpCloudStorageConnection, GcpCredentialManager
from phdi.tabulation.tables import validate_schema
import jsonschema


cloud_providers = {
    "azure": AzureCloudContainerConnection,
    "gcp": GcpCloudStorageConnection,
}
cred_managers = {"azure": AzureCredentialManager, "gcp": GcpCredentialManager}


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


def get_cred_manager(
    cred_manager: str, location_url: str = None
) -> BaseCredentialManager:
    """
    Return a credential manager for different cloud providers depending upon which
    one the user requests via the parameter.

    :param credential_manager: A string identifying which cloud credential
    manager is desired.
    :return: Either a Google Cloud Credential Manager or an Azure Credential Manager
    depending upon the value passed in.
    """
    cred_manager_class = cred_managers.get(cred_manager)
    result = None
    # if the cred_manager_class is not none then instantiate an instance of it
    if cred_manager_class is not None:
        if cred_manager == "azure":
            result = cred_manager_class(resource_location=location_url)
        else:
            result = cred_manager_class()

    return result


def check_schema_validity(value: dict):
    valid = True
    try:
        validate_schema(value)
    except jsonschema.exceptions.ValidationError:
        valid = False
    assert valid is True, "Must provide a valid schema."
    return value
