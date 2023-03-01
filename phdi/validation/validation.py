import re
from lxml import etree


namespaces = {
    "hl7": "urn:hl7-org:v3",
    "xsi": "http://www.w3.org/2005/Atom",
    "cda": "urn:hl7-org:v3",
    "sdtc": "urn:hl7-org:sdtc",
    "voc": "http://www.lantanagroup.com/voc",
}


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
        matched_xml_elements = _match_nodes(
            xml_elements=parsed_ecr.xpath(cda_path, namespaces=namespaces),
            config_field=field,
        )
        if not matched_xml_elements:
            error_message = "Could not find field: " + str(field)
            error_messages.append(error_message)
            continue

        for xml_element in matched_xml_elements:
            error_messages += _validate_attribute(xml_element, field)
            error_messages += _validate_text(field, xml_element)

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


def _match_nodes(xml_elements, config_field) -> list:
    """
    Matches the xml_elements to the config fields attributes and parent
    attributes. Returns list of matching fields

    :param xml_elements: A list of xml elements
    :param config_field: A dictionay of the requrements of the field.
    """
    if not xml_elements:
        return []
    matching_elements = []
    for xml_element in xml_elements:
        if config_field.get("parent"):
            parent_element = xml_element.getparent()

            # Account for the possibility that we want a parent but none are found
            if parent_element is None:
                continue
            parent_config = {
                "fieldName": config_field.get("parent"),
                "attributes": config_field.get("parent_attributes"),
                "cdaPath": config_field.get("cdaPath")
                + ":"
                + config_field.get("parent"),
            }

            parent_found = _check_field_matches(parent_element, parent_config)

            # If we didn't find the parent, or it has the wrong attributes,
            # go to the next xml element
            if (not parent_found) or _validate_attribute(parent_element, parent_config):
                continue
        found = _check_field_matches(xml_element, config_field)
        if found:
            matching_elements.append(xml_element)
    return matching_elements


def _check_field_matches(xml_element, config_field):
    # If it has the wrong field name, go to the next one
    field_name = re.search(r"(?!\:)[a-zA-z]+\w$", config_field.get("cdaPath")).group(0)
    if field_name.lower() not in xml_element.tag.lower():
        return False
    # Check if it has the right attributes
    field_attributes = config_field.get("attributes")
    if field_attributes:
        # For each attribute see if it has a regEx and match it
        for attribute in field_attributes:
            # If field is supposed to have an attribute and doesn't,
            # return not field not found.
            if not xml_element.get(attribute.get("attributeName")):
                return False
    else:
        if xml_element.attrib:
            return False
    return True


def _validate_attribute(node, field) -> list:
    """
    Validates a node by checking if attribute exists or matches regex pattern.
    If the node does not pass a test as described in the config, an error message is
    appended. All fields are valid if the error message list is blank

    :param field: A dictionary entry that describes what fields need to be
        validated and how
    :param node: A dictionary entry that includes the attribute name key and
        value.
    """
    if not field.get("attributes"):
        return []

    attribute_value = ""
    error_messages = []
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
            if (not attribute_value) or (not pattern.match(attribute_value)):
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
    if not field.get("textRequired"):
        return []

    text = "".join(node.itertext())
    regEx = field.get("regEx")
    if regEx is not None:
        pattern = re.compile(regEx)
        if pattern.match(text) is None:
            return [
                "Field: "
                + field.get("fieldName")
                + " does not match regEx: "
                + field.get("regEx")
            ]
        else:
            return []
    else:
        if text is not None:
            return []
        else:
            return ["Field: " + field.get("fieldName") + " does not have text"]
