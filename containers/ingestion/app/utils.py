import json
import pathlib
from typing import Optional
from typing import Union

from pydantic import BaseModel
from pydantic import Field
from pydantic import root_validator

from app.cloud.azure import AzureCloudContainerConnection
from app.cloud.azure import AzureCredentialManager
from app.cloud.core import BaseCredentialManager
from app.cloud.gcp import GcpCloudStorageConnection
from app.cloud.gcp import GcpCredentialManager
from app.config import get_settings


class StandardResponse(BaseModel):
    """The standard schema for the body of responses returned by the DIBBs Ingestion
    Service."""

    status_code: str = Field(description="The HTTP status code of the response.")
    message: Optional[Union[str, dict]] = Field(
        description="A message from the service, used to provide details on an error "
        "that was encounted while attempting the process a request, or the response "
        "a FHIR server."
    )
    bundle: Optional[dict] = Field(description="A FHIR bundle")

    @root_validator
    def any_of(cls, values):
        """
        Validates that at least one of the specified fields is present.

        :param cls: The class on which this validator is defined.
        :param values: The dictionary of field values to validate.
        :return: The original dictionary of values if validation passes.
        """
        if not any(value in values for value in ["message", "bundle"]):
            raise ValueError(
                "A value for at least 'message' or 'bundle' must be provided"
            )
        return values


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
    Found in the environment not present in the input dictionary that are
    found in the environment are added to the dictionary. A message is
    returned indicating which, if any, required values could not be found.

    :param input: A dictionary potentially originating from the body of a POST
        request
    :param required_values: A list of values to search for in the input
        dictionary and the environment.
    :return: A string message indicating if any required values could not be
        found and if so which ones.
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
    Return a credential manager for different cloud providers depending upon
    which one the user requests via the parameter.

    :param credential_manager: A string identifying which cloud credential
    manager is desired.
    :return: Either a Google Cloud Credential Manager or an Azure Credential
        Manager depending upon the value passed in.
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


def get_cloud_provider_storage_connection(
    cloud_provider: str, storage_account_url: str = None
) -> BaseCredentialManager:
    """
    Return a cloud provider storage connection for different cloud providers
    depending upon which one the user requests via the parameter.

    :param cloud_provider: A string identifying which cloud provider is
        desired.
    :return: Either a Google Cloud Storage Connection or an Azure Storage
    Connection depending upon the value passed in.
    """
    cloud_provider_class = cloud_providers.get(cloud_provider)
    result = None
    # if the cloud_provider_class is not none then instantiate an instance of it
    if cloud_provider_class is not None:
        if cloud_provider == "azure":
            cred_manager = get_cred_manager(
                cred_manager=cloud_provider, location_url=storage_account_url
            )
            result = cloud_provider_class(
                storage_account_url=storage_account_url, cred_manager=cred_manager
            )
        else:
            result = cloud_provider_class()
    return result


def read_json_from_assets(filename: str):
    """
    Loads and returns the content of a JSON file from the 'assets' directory.

    :param filename: The name of the JSON file to be loaded.
    :return: The content of the JSON file as a dictionary.
    """
    return json.load(open((pathlib.Path(__file__).parent.parent / "assets" / filename)))
