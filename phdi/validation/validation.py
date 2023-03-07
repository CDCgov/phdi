import re
from lxml import etree


namespaces = {
    "hl7": "urn:hl7-org:v3",
    "xsi": "http://www.w3.org/2005/Atom",
    "cda": "urn:hl7-org:v3",
    "sdtc": "urn:hl7-org:sdtc",
    "voc": "http://www.lantanagroup.com/voc",
}


def validate_ecr(ecr_message: str, config: dict, include_error_types: list) -> dict:
    error_messages = {"fatal": [], "errors": [], "warnings": [], "information": []}
    # encoding ecr_message to allow it to be
    #  parsed and organized as an lxml Element Tree Object
    xml = ecr_message.encode("utf-8")
    parser = etree.XMLParser(ns_clean=True, recover=True, encoding="utf-8")

    # we need a try-catch around this to ensure that the ecr message
    # passed in is proper XML - also ensure it's a clinical document
    try:
        parsed_ecr = etree.fromstring(xml, parser=parser)
        parsed_ecr.xpath("//hl7:ClinicalDocument", namespaces=namespaces)
    except AttributeError:
        error_messages["fatal"].append("eCR Message is not valid XML!")
        _response_builder(
            errors=error_messages, msg=None, include_error_types=include_error_types
        )

    for field in config.get("fields"):
        cda_path = field.get("cdaPath")
        matched_xml_elements = _match_nodes(
            xml_elements=parsed_ecr.xpath(cda_path, namespaces=namespaces),
            config_field=field,
        )
        message_type = (
            field.get("errorType")
            if field.get("errorType") in error_messages.keys()
            else "errors"
        )

        if not matched_xml_elements:
            error_message = "Could not find field: " + str(field)
            error_messages[message_type].append(error_message)
            continue

        for xml_element in matched_xml_elements:
            error_messages[message_type] += _validate_attribute(xml_element, field)
            error_messages[message_type] += _validate_text(xml_element, field)

    response = _response_builder(
        errors=error_messages, msg=ecr_message, include_error_types=include_error_types
    )
    return response


def _organize_error_messages(
    fatal: list,
    errors: list,
    warnings: list,
    information: list,
    include_error_types: list,
) -> dict:
    # utilize the error_types to filter out the different error message
    # types as well as specify the difference between the different error types
    # during the validation process

    # fatal warnings cannot be filtered and will be automatically included!

    if "errors" in include_error_types:
        filtered_errors = errors
    else:
        filtered_errors = []

    if "warnings" in include_error_types:
        filtered_warnings = warnings
    else:
        filtered_warnings = []

    if "information" in include_error_types:
        filtered_information = information
    else:
        filtered_information = []

    organized_messages = {
        "fatal": fatal,
        "errors": filtered_errors,
        "warnings": filtered_warnings,
        "information": filtered_information,
    }
    return organized_messages


def _match_nodes(xml_elements, config_field) -> list:
    """
    Matches the xml_elements to the config fields attributes and parent
    attributes. Returns list of matching fields

    :param xml_elements: A list of xml elements
    :param config_field: A dictionary of the requirements of the field.
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


def _validate_attribute(xml_element, config_field) -> list:
    """
    Validates a node by checking if attribute exists or matches regex pattern.
    If the node does not pass a test as described in the config, an error message is
    appended. All fields are valid if the error message list is blank

    :param field: A dictionary entry that describes what fields need to be
        validated and how
    :param node: A dictionary entry that includes the attribute name key and
        value.
    """
    if not config_field.get("attributes"):
        return []

    attribute_value = ""
    error_messages = []
    for attribute in config_field.get("attributes"):
        if "attributeName" in attribute:
            attribute_name = attribute.get("attributeName")
            attribute_value = xml_element.get(attribute_name)
            if not attribute_value:
                error_messages.append(
                    f"Could not find attribute {attribute_name} "
                    + f"for tag {config_field.get('fieldName')}"
                )
        if "regEx" in attribute:
            pattern = re.compile(attribute.get("regEx"))
            if (not attribute_value) or (not pattern.match(attribute_value)):
                field_name = config_field.get("fieldName")
                error_messages.append(
                    f"Attribute: '{attribute_name}' for field: '{field_name}'"
                    + " not in expected format"
                )
    return error_messages


def _validate_text(xml_element, config_field):
    """
    Validates a node text by checking if it has a parent that matches the schema.
    Then it validates that the text of the node matches is there or matches the
    regEx listed in the schema

    :param field: A dictionary entry that describes what fields need to be
        validated and how
    :param node: A dictionary entry that includes the attribute name key and
        value.
    """
    if not config_field.get("textRequired"):
        return []

    text = "".join(xml_element.itertext())
    regEx = config_field.get("regEx")
    if regEx is not None:
        pattern = re.compile(regEx)
        if pattern.match(text) is None:
            return [
                "Field: "
                + config_field.get("fieldName")
                + " does not match regEx: "
                + config_field.get("regEx")
            ]
        else:
            return []
    else:
        if text is not None and text != "":
            return []
        else:
            return ["Field: " + config_field.get("fieldName") + " does not have text"]


def _response_builder(errors: dict, msg: str, include_error_types: list) -> dict:
    if errors.get("fatal") != []:
        valid = False
    else:
        valid = True
        errors["information"].append("Validation completed with no fatal errors!")

    if valid:
        validated_message = msg
    else:
        validated_message = None

    return {
        "message_valid": valid,
        "validation_results": _organize_error_messages(
            fatal=errors["fatal"],
            errors=errors["errors"],
            warnings=errors["warnings"],
            information=errors["information"],
            include_error_types=include_error_types,
        ),
        "validated_message": validated_message,
    }
