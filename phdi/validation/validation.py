from io import StringIO
import json
import os
import pathlib
import re
from lxml import etree
import yaml

namespaces = {
    "hl7": "urn:hl7-org:v3",
    "xsi": "http://www.w3.org/2005/Atom",
    "cda": "urn:hl7-org:v3",
    "sdtc": "urn:hl7-org:sdtc",
    "voc": "http://www.lantanagroup.com/voc",
}


# TODO: Determine where/when this configuration should be loaded (as we
# will only want to load this once or after it has been updated instead
# of loading it each time we validate an eCR)
# we may also need to move this to a different location depending upon where/when
# the loading occurs
def load_config(path: pathlib.Path) -> dict:
    """
    Given the path to a local YAML or JSON file containing a validation
    configuration, loads the file and returns the resulting validation
    configuration as a dictionary. If the file can't be found, raises an error.

    :param path: The file path to a YAML file holding a validation configuration.
    :raises ValueError: If the provided path points to an unsupported file type.
    :raises FileNotFoundError: If the file to be loaded could not be found.
    :raises JSONDecodeError: If a JSON file is provided with invalid JSON.
    :return: A dict representing a validation configuration read
        from the given path.
    """
    try:
        with open(path, "r") as file:
            if path.suffix == ".yaml":
                config = yaml.safe_load(file)
            elif path.suffix == ".json":
                config = json.load(file)
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
    except json.decoder.JSONDecodeError as e:
        raise json.decoder.JSONDecodeError(
            "The specified file is not valid JSON.", e.doc, e.pos
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


def validate_ecr(ecr_message: str, config_path: str, error_types: list) -> dict:
    # TODO: remove the hard coding of the location of the config file
    # and utilize the location passed in...OR we could use a specified
    # location for the config file with a particular name that we would utilize
    if config_path is None:
        curr_path = os.path.dirname(__file__)
        config_path = os.path.relpath("..\\config\\sample_config.yaml", curr_path)
    config = load_config(path=config_path)
    # first convert the ecr_message into stringIO which
    # which can then be used by the etree parse function
    # that creates an ElementTree object - if you just
    # use etree.XML() it only creates an Element object
    ecr = StringIO(ecr_message)
    parsed_ecr = etree.parse(ecr)

    # TODO: utilize the error_types to filter out the different error message
    # types as well as specify the difference between the different error types
    # during the validation process

    error_messages = []
    messages = []
    for field in config.get("requiredFields"):
        cda_path = field.get("cdaPath")
        matched_nodes = parsed_ecr.xpath(cda_path, namespaces=namespaces)

        for node in matched_nodes:
            # TODO: Evaluate if textRequired check should be done up here or
            # in the function
            # TODO: This needs to be cleaned up
            if field.get("textRequired"):
                # text check
                found, text_error_messages = _validate_text(field, node)
                for error in text_error_messages:
                    error_messages.append(error)
            elif field.get("attributes"):
                # attributes check
                attribute_error_messages = _validate_attribute(field, node)
                for error in attribute_error_messages:
                    error_messages.append(error)
    if error_messages:
        valid = False
    else:
        valid = True
        messages.append("Validation complete with no errors!")

    response = {
        "message_valid": valid,
        "validation_results": _organize_messages(
            errors=error_messages, warnings=[], information=messages
        ),
    }
    return response


def _organize_messages(errors: list, warnings: list, information: list) -> dict:
    organized_messages = {
        "errors": errors,
        "warnings": warnings,
        "information": information,
    }
    return organized_messages


def _validate_attribute(field, node) -> list:
    """
    Validates a node by checking if attribute exists or matches regex pattern.
    If the node does not pass a test as described in the config, an error message is
    appended. All fields are valid if the error message list is blank

    :param field: A dictionary entry that describes what fields need to be
        validated and how
    :param node: A dictionary entry that includes the attribute name key and
        value.
    """
    attribute_value = ""
    error_messages = []
    # TODO: remove when we refactor
    if field.get("textRequired") or not field.get("attributes"):
        return []
    for attribute in field.get("attributes"):
        if "attributeName" in attribute:
            attribute_name = attribute.get("attributeName")
            attribute_value = node.get(attribute_name)
            if not attribute_value:
                error_messages.append(
                    f"Could not find attribute {attribute_name} "
                    + f"for tag {field.get('fieldName')}"
                )
        if "regEx" in attribute:
            pattern = re.compile(attribute.get("regEx"))

            if not attribute_value or pattern.match(attribute_value):
                error_messages.append(
                    f"Attribute '{attribute_name}' not in expected format"
                )
    return error_messages


def _validate_text(field, node):
    """
    Validates a node text by checking if it has a parent that matches the schema.
    Then it validates that the text of the node matches is there or matches the
    regEx listed in the schema

    :param field: A dictionary entry that describes what fields need to be
        validated and how
    :param node: A dictionary entry that includes the attribute name key and
        value.
    """
    if field.get("textRequired"):
        found = False
        parent_found = False
        parent_node = node.getparent() if field.get("parent") else None
        # If there is no parent, just set parent found to true
        if parent_node is None:
            parent_found, error_messages_parents = (True, [])
        else:
            parent_found, error_messages_parents = _field_matches(
                {
                    "fieldName": field.get("parent"),
                    "attributes": field.get("parent_attributes"),
                    "cdaPath": field.get("cdaPath") + ":" + field.get("parent"),
                },
                parent_node,
            )
        found, error_messages = _field_matches(field, node)
        error_messages += error_messages_parents
        if found is not True or parent_found is not True:
            return (False, error_messages)
        if error_messages:
            return (True, error_messages)
        else:
            return (True, [])


def _field_matches(field, node):
    # If it has the wrong parent, go to the next one
    fieldName = re.search(r"(?!\:)[a-zA-z]+\w$", field.get("cdaPath")).group(0)
    if fieldName.lower() not in node.tag.lower():
        return (False, [])
    # Check if it has the right attributes
    if field.get("attributes"):
        attributes_dont_match = []
        field_attributes = field.get("attributes")
        if field_attributes:
            for attribute in field_attributes:
                # For each attribute see if it has a regEx and match it
                if attribute.get("regEx"):
                    pattern = re.compile(attribute.get("regEx"))
                    text = node.get(attribute.get("attributeName"))
                    text = text if text is not None else ""
                    if not pattern.match(text):
                        attributes_dont_match.append(
                            "Attribute: "
                            + attribute.get("attributeName")
                            + " does not match regex"
                        )
                else:
                    if not field.get(attribute.get("attributeName")):
                        attributes_dont_match.append(
                            "Attribute: "
                            + attribute.get("attributeName")
                            + " not found"
                        )
            if attributes_dont_match:
                return (False, [])
    else:
        if node.attrib:
            return (False, [])
    if field.get("textRequired") is not None:
        text = "".join(node.itertext())
        regEx = field.get("regEx")
        if regEx is not None:
            pattern = re.compile(regEx)
            if pattern.match(text) is None:
                return (
                    True,
                    [
                        "Field: "
                        + field.get("fieldName")
                        + " does not match regEx: "
                        + field.get("regEx")
                    ],
                )
            else:
                return (True, [])
        else:
            if text is not None:
                return (True, [])
            else:
                return (
                    True,
                    ["Field: " + field.get("fieldName") + " does not have text"],
                )
    return (True, [])
