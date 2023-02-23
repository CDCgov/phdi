import pathlib
import yaml

VALID_ERROR_TYPES = ["error", "warn", "info"]


# TODO: Determine where/when this configuration should be loaded (as we
# will only want to load this once or after it has been updated instead
# of loading it each time we validate an eCR)
# we may also need to move this to a different location depending upon where/when
# the loading occurs
def load_config(path: pathlib.Path) -> dict:
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
    try:
        with open(path, "r") as file:
            if path.suffix == ".yaml":
                config = yaml.safe_load(file)
            else:
                ftype = path.suffix.replace(".", "").upper()
                raise ValueError(f"Unsupported file type provided: {ftype}")
        # TODO:
        # Create a file that validates the validation configuration created
        # by the client
        # validate_config(config)
        return config
    except FileNotFoundError:
        raise FileNotFoundError(
            "The specified file does not exist at the path provided."
        )


# def validate_config(config: dict):
#     """
#     Validates the validation configuration structure, ensuring
#     all required validation elements are present and all configuration
#     elements are of the expected data type.

#     :param config: A declarative, user-defined configuration for validating
#         data fields within a message (ecr, elr, vxu).
#     :raises jsonschema.exception.ValidationError: If the schema is invalid.
#     """
#     # TODO:
#     # Create a file that validates the validation configuration created
#     # by the client
#     with importlib.resources.open_text(
#         "phdi.tabulation", "validation_schema.json"
#     ) as file:
#         validation_schema = json.load(file)

#     validate(schema=validation_schema, instance=config)


def validate_error_types(error_types: str) -> str:
    """
    Given a string of comma separated of error types ensure they are valid.
    If they aren't, remove them from the string.  

    :param error_types: A comma separated string of error types.
    :return: A valid comma separate list of error types in a string.
    """
    if error_types is None or error_types == "":
        return ""

    validated_error_types = []

    for et in error_types.split(','):
        if et in VALID_ERROR_TYPES:
            validated_error_types.append(et)

    return ",".join(validated_error_types)
