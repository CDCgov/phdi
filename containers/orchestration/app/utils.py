import json
import pathlib
from functools import cache
from pathlib import Path
from frozendict import frozendict
from phdi.cloud.azure import AzureCredentialManager
from phdi.cloud.core import BaseCredentialManager
from phdi.cloud.gcp import GcpCredentialManager


@cache
def load_processing_schema(schema_name: str) -> dict:
    """
    Load a processing schema given its name. Look in the 'custom_schemas/' directory
    first. If no custom schemas match the provided name, check the schemas provided by
    default with this service in the 'default_schemas/' directory.

    :param path: The path to an extraction schema file.
    :return: A dictionary containing the extraction schema.
    """
    custom_schema_path = Path(__file__).parent / "custom_schemas" / schema_name
    try:
        with open(custom_schema_path, "r") as file:
            processing_schema = json.load(file)
    except FileNotFoundError:
        try:
            default_schema_path = (
                Path(__file__).parent / "default_schemas" / schema_name
            )
            with open(default_schema_path, "r") as file:
                processing_schema = json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"A schema with the name '{schema_name}' could not be found."
            )

    return freeze_processing_schema(processing_schema)


def freeze_processing_schema(processing_schema: dict) -> frozendict:
    """
    Given a processing schema dictionary, freeze it and all of its nested dictionaries
    into a single immutable dictionary.

    :param processing_schema: A dictionary containing a processing schema.
    :return: A frozen dictionary containing the processing schema.
    """
    for field, field_definition in processing_schema.items():
        if "secondary_schema" in field_definition:
            for secondary_field, secondary_field_definition in field_definition[
                "secondary_schema"
            ].items():
                field_definition["secondary_schema"][secondary_field] = frozendict(
                    secondary_field_definition
                )
            field_definition["secondary_schema"] = frozendict(
                field_definition["secondary_schema"]
            )
        processing_schema[field] = frozendict(field_definition)
    return frozendict(processing_schema)


credential_managers = {"azure": AzureCredentialManager, "gcp": GcpCredentialManager}


def get_credential_manager(
    credential_manager: str, location_url: str = None
) -> BaseCredentialManager:
    """
    Return a credential manager for different cloud providers depending upon which
    one the user requests via the parameter.

    :param credential_manager: A string identifying which cloud credential
    manager is desired.
    :return: Either a Google Cloud Credential Manager or an Azure Credential Manager
    depending upon the value passed in.
    """
    credential_manager_class = credential_managers.get(credential_manager)
    result = None
    # if the credential_manager_class is not none then instantiate an instance of it
    if credential_manager_class is not None:
        if credential_manager == "azure":
            result = credential_manager_class(resource_location=location_url)
        else:
            result = credential_manager_class()

    return result


def read_json_from_assets(filename: str):
    return json.load(open((pathlib.Path(__file__).parent.parent / "assets" / filename)))
