import re
from lxml import etree


namespaces = {
    "hl7": "urn:hl7-org:v3",
    "xsi": "http://www.w3.org/2005/Atom",
    "cda": "urn:hl7-org:v3",
    "sdtc": "urn:hl7-org:sdtc",
    "voc": "http://www.lantanagroup.com/voc",
}


def validate_config():
    pass


def validate_ecr(ecr_message: str, config: dict, error_types: str) -> dict:
    xml = ecr_message.encode("utf-8")
    parser = etree.XMLParser(ns_clean=True, recover=True, encoding="utf-8")
    parsed_ecr = etree.fromstring(xml, parser=parser)

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
