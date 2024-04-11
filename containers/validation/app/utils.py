import json
import pathlib
import re

import yaml
from fastapi import HTTPException
from fastapi import status
from lxml.etree import XMLSyntaxError

from app.fhir.conversion import add_rr_data_to_eicr

VALID_ERROR_TYPES = ["fatal", "errors", "warnings", "information"]
# TODO: remove the hard coding of the location of the config file
# and utilize the location passed in...OR we could use a specified
# location for the config file with a particular name that we would utilize
DEFAULT_CONFIG_PATH = pathlib.Path(__file__).parent.parent / "config"
# / "sample_ecr_config.yaml"


# TODO: Determine where/when this configuration should be loaded (as we
# will only want to load this once or after it has been updated instead
# of loading it each time we validate an eCR)
# we may also need to move this to a different location depending upon where/when
# the loading occurs
def load_ecr_config(file_path: pathlib.Path = None) -> dict:
    """
    Given the path to a local YAML file containing a validation
    configuration, loads the file and returns the resulting validation
    configuration as a dictionary. If the file can't be found, raises an error.

    :param path: The file path to a YAML file holding a validation configuration.
    :raises ValueError: If the provided path points to an unsupported file type.
    :raises FileNotFoundError: If the file to be loaded could not be found.
    :return: A dict representing a validation configuration read
        from the given path.
    """
    path = DEFAULT_CONFIG_PATH / "sample_ecr_config.yaml"

    # first check if there is a STLT defined config.yaml
    # if not, then just use the default sample_ecr_config.yaml
    for file in pathlib.Path(DEFAULT_CONFIG_PATH).glob("*.yaml"):
        file_name = pathlib.Path(file).stem
        if file_path is None and re.search("^ecr_config_[a-z]+", file_name.lower()):
            path = DEFAULT_CONFIG_PATH / file
            exit
        elif file_path is not None:
            path = file_path

    try:
        with open(path, "r") as file:
            if path.suffix == ".yaml":
                config = yaml.safe_load(file)
                if not validate_config(config):
                    raise ValueError(
                        "The configuration file supplied: " + f"{path} is invalid!"
                    )
            else:
                ftype = path.suffix.replace(".", "").upper()
                raise ValueError(f"Unsupported file type provided: {ftype}")
        return config
    except FileNotFoundError:
        raise FileNotFoundError(
            "The specified file does not exist at the path provided."
        )


def validate_error_types(error_types: str) -> list:
    """
    Given a string of comma separated of error types ensure they are valid.
    If they aren't, remove them from the string.

    :param error_types: A comma separated string of error types.
    :return: A valid list of error types in a string.
    """
    if error_types is None or error_types == "":
        return []

    validated_error_types = []

    for et in error_types.split(","):
        if et in VALID_ERROR_TYPES:
            validated_error_types.append(et)

    return validated_error_types


def validate_config(config: dict):
    """
    #     # TODO:
    #     # Create a file that validates the validation configuration created
    #     # by the client - example below
    #     with importlib.resources.open_text(
    #         "phdi.tabulation", "validation_schema.json"
    #     ) as file:
    #         validation_schema = json.load(file)

    #     validate(schema=validation_schema, instance=config)
    """
    if not config.get("fields"):
        return False
    for field in config.get("fields"):
        if not all(key in field for key in ("fieldName", "cdaPath", "errorType")):
            return False
        if "attributes" not in field and "textRequired" not in field:
            return False
    return True


def check_for_and_extract_rr_data(input: dict):
    """
    Checks the input for Reportability Response (RR) data and merges it into
    the electronic Initial Case Report (eICR) message if present.

    :param input: A dictionary containing the message details. Expected keys
        are 'rr_data', 'message_type', and 'message'. 'rr_data' should contain
        the RR XML data, 'message_type' should specify the type of the message,
        and 'message' should contain the eICR XML data.
    :return: The updated input dictionary with the 'message' key now containing
        the merged eICR and RR data if applicable.
    :raises HTTPException: If RR data is provided for a non-'ecr' message type
        or if either the RR data or the eICR message is not valid XML.
    """
    if input["rr_data"] is not None:
        if input["message_type"] != "ecr":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Reportability Response (RR) data is only "
                "accepted for eCR validation requests.",
            )

        try:
            merged_ecr = add_rr_data_to_eicr(input["rr_data"], input["message"])
            input["message"] = merged_ecr
        except XMLSyntaxError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Reportability Response and eICR message both "
                "must be valid XML messages.",
            )

    return input


def read_json_from_assets(filename: str):
    """
    Reads and returns the content of a JSON file from the assets directory
    as a dictionary.

    :param filename: Name of the JSON file, including the '.json' extension.
    :return: Content of the JSON file.
    :raises FileNotFoundError: If the file is not in the assets directory.
    :raises JSONDecodeError: If the file content is not valid JSON.
    """
    return json.load(open((pathlib.Path(__file__).parent.parent / "assets" / filename)))
