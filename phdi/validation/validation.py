import re
from lxml import etree


namespaces = {
    "hl7": "urn:hl7-org:v3",
    "xsi": "http://www.w3.org/2005/Atom",
    "cda": "urn:hl7-org:v3",
    "sdtc": "urn:hl7-org:sdtc",
    "voc": "http://www.lantanagroup.com/voc",
}

EICR_MSG_ID_XPATH = "//hl7:ClinicalDocument/hl7:id"
RR_MSG_ID_XPATH = "//hl7:ClinicalDocument/hl7:section/hl7:id"


def validate_ecr(ecr_message: str, config: dict, include_error_types: list) -> dict:
    error_messages = {
        "fatal": [],
        "errors": [],
        "warnings": [],
        "information": [],
        "message_ids": {},
    }
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
        return _response_builder(
            errors=error_messages, msg=None, include_error_types=include_error_types
        )

    # first get the message id for the eicr and the rr
    xml_eicr_id = _get_xml_message_id(
        parsed_ecr.xpath(EICR_MSG_ID_XPATH, namespaces=namespaces)
    )
    xml_rr_id = _get_xml_message_id(
        parsed_ecr.xpath(RR_MSG_ID_XPATH, namespaces=namespaces)
    )
    message_ids = {"eicr": xml_eicr_id, "rr": xml_rr_id}
    error_messages["message_ids"] = message_ids

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
            error_message = "Could not find field. " + _get_field_details_string(
                None, field
            )
            error_messages[message_type].append(error_message)
            continue
        attribute_errors = []
        text_errors = []
        for xml_element in matched_xml_elements:
            attribute_errors += _validate_attribute(xml_element, field)
            text_errors += _validate_text(xml_element, field)
        if not (
            field.get("validateOne")
            and len(attribute_errors) < len(matched_xml_elements)
            and len(text_errors) < len(matched_xml_elements)
        ):
            error_messages[message_type] += attribute_errors
            error_messages[message_type] += text_errors
    response = _response_builder(
        errors=error_messages, msg=ecr_message, include_error_types=include_error_types
    )
    return response


def _get_field_details_string(xml_element, config_field) -> str:
    """
    Gets the name, value, of the field referenced as well as the details of the
    relatives and formats it into a string for use in messages

    :param xml_element: An xml element.
    :param config_field: A dictionary of the requirements of the field.
    """
    name = [f"Field name: '{config_field.get('fieldName')}'"]
    config_attributes = config_field.get("attributes")
    attributes = (
        ["Attributes:"] + _get_attributes_list(config_attributes, xml_element)
        if config_attributes
        else []
    )
    relatives = config_field.get("relatives")
    relative_string = []
    if relatives:
        relative_string.append("Related elements:")
        for config in relatives:
            relative_field_name = config.get("name")
            relative_name = (
                ["Field name: '" + relative_field_name + "'"]
                if relative_field_name
                else []
            )
            config_related_attributes = config_field.get("attributes")
            element = _find_related_element(
                xml_element, config_field.get("cdaPath"), config
            )
            relative_attributes = (
                ["Attributes:"]
                + _get_attributes_list(config_related_attributes, element)
                if config_related_attributes
                else []
            )
            relative_string += relative_name
            relative_string += relative_attributes

    value = (
        [f"value: '{''.join(xml_element.itertext())}'"]
        if config_field.get("textRequired") and xml_element is not None
        else []
    )
    return " ".join(name + value + attributes + relative_string)


def _get_attributes_list(attributes, xml_element) -> list:
    attrs = []
    for attribute in attributes:
        attribute_name = attribute.get("attributeName")
        reg_ex = attribute.get("regEx")
        reg_ex_string = f" RegEx: '{reg_ex}'" if reg_ex else ""

        if xml_element is not None and xml_element.get(attribute_name):
            attribute_value = f" value: '{xml_element.get(attribute_name)}'"
        else:
            attribute_value = ""

        attrs.append(f"name: '{attribute_name}'{reg_ex_string}{attribute_value}")
    return [", ".join(attrs)]


def _organize_error_messages(
    fatal: list,
    errors: list,
    warnings: list,
    information: list,
    message_ids: dict,
    include_error_types: list,
) -> dict:
    # utilize the error_types to filter out the different error message
    # types as well as specify the difference between the different error types
    # during the validation process

    # fatal warnings cannot be filtered and will be automatically included!

    filtered_errors = errors if "errors" in include_error_types else []
    filtered_warnings = warnings if "warnings" in include_error_types else []
    filtered_information = information if "information" in include_error_types else []

    organized_messages = {
        "fatal": fatal,
        "errors": filtered_errors,
        "warnings": filtered_warnings,
        "information": filtered_information,
        "message_ids": message_ids,
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
        if not _check_relatives(xml_element, config_field):
            continue
        found = _check_field_matches(xml_element, config_field)

        if found:
            matching_elements.append(xml_element)
    return matching_elements


def _find_related_element(xml_element, cda_path, config_field):
    """
    Returns an xml element that is related to another xml element based on
    the cda_path of the element you are searching for

    :param xml_elements: A list of xml elements
    :param cda_path: A string representing the location of the item being looked for.
    :param config_field: A dictionary of the requirements of the field.
    """
    if xml_element is None:
        return False
    relative = config_field
    relative_cda_path = relative.get("cdaPath")
    relative_tag_name = re.search(r"(?!\:)[a-zA-z]+\w$", relative.get("cdaPath")).group(
        0
    )

    iter = _get_iterator(cda_path, relative_cda_path, xml_element)
    elements = []
    for e in iter:
        if relative_tag_name in e.tag:
            elements.append(e)

    if elements is None or len(elements) == 0:
        return False
    for element in elements:
        relative_config = {
            "fieldName": relative.get("name"),
            "attributes": relative.get("attributes"),
            "cdaPath": relative.get("cdaPath"),
        }
        relative_found = _check_field_matches(element, relative_config)
        if (not relative_found) or _validate_attribute(element, relative_config):
            return False
        else:
            return element


def _get_iterator(cda_path, relative_cda_path, xml_element):
    """
    Gets an iterator or list for elements based on the main element path and the element
    path being searched for.

    :param cda_path: A string representing the location of the item being looked for.
    :param relative_cda_path: A string representing the path of the item to be searched
    for.
    :param xml_element: The xml_element that is being used to find the relative
    """
    diff = _diff_split(cda_path, relative_cda_path)
    # element is on the same level of the main element
    if diff == 0:
        iter = []
        iter_forward = xml_element.itersiblings()
        iter_reverse = xml_element.itersiblings(preceding=True)
        for e in iter_forward:
            iter.append(e)
        for e in iter_reverse:
            iter.append(e)
        return iter
    # element is a parent to the main element
    elif diff > 0:
        return xml_element.iterancestors()
    # element is a child of the main element
    else:
        return xml_element.iterchildren()


def _diff_split(str, second_str, splitter="/") -> int:
    return len(str.split(splitter)) - len(second_str.split(splitter))


def _check_relatives(xml_element, config_field) -> bool:
    relatives = config_field.get("relatives")
    if relatives is None:
        return True
    for relative in relatives:
        if (
            _find_related_element(xml_element, config_field.get("cdaPath"), relative)
            is False
        ):
            return False
    return True


def _check_field_matches(xml_element, config_field):
    # If it has the wrong field name, go to the next one
    field_name = re.search(r"(?!\:)[a-zA-z]+\w$", config_field.get("cdaPath")).group(0)

    if field_name.lower() not in xml_element.tag.lower():
        return False
    # Don't match attributes if we are validating all fields

    match_attributes = False if config_field.get("validateAll") == "True" else True
    if not match_attributes:
        return True
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
                message = _check_custom_message(
                    config_field,
                    f"Could not find attribute {attribute_name}. "
                    + f"{_get_field_details_string(xml_element, config_field)}",
                )
                error_messages.append(message)
        if "regEx" in attribute:
            pattern = re.compile(attribute.get("regEx"))
            if (not attribute_value) or (not pattern.match(attribute_value)):
                message = _check_custom_message(
                    config_field,
                    f"Attribute: '{attribute_name}'"
                    + " not in expected format. "
                    + f"{_get_field_details_string(xml_element, config_field)}",
                )
                error_messages.append(message)

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
            message = _check_custom_message(
                config_field,
                "Field does not match regEx: "
                + config_field.get("regEx")
                + f". {_get_field_details_string(xml_element, config_field)}",
            )
            return [message]
        else:
            return []
    else:
        if text is not None and text != "":
            return []
        else:
            message = _check_custom_message(
                config_field,
                "Field does not have text. "
                + f"{_get_field_details_string(xml_element, config_field)}",
            )
            return [message]


def _response_builder(errors: dict, msg: str, include_error_types: list) -> dict:
    if errors.get("fatal") != []:
        valid = False
    else:
        valid = True
        errors["information"].append("Validation completed with no fatal errors!")

    validated_message = msg if valid else None

    return {
        "message_valid": valid,
        "validation_results": _organize_error_messages(
            fatal=errors["fatal"],
            errors=errors["errors"],
            warnings=errors["warnings"],
            information=errors["information"],
            message_ids=errors["message_ids"],
            include_error_types=include_error_types,
        ),
        "validated_message": validated_message,
    }


def _check_custom_message(config_field, default_message):
    message = default_message
    if config_field.get("customMessage"):
        message = config_field.get("customMessage")
    return message


def _get_xml_message_id(id_xml_tag: etree.Element) -> dict:
    if id_xml_tag == []:
        return {}
    id_root = id_xml_tag[0].get("root")
    id_extension = id_xml_tag[0].get("extension")
    message_id = {"root": id_root, "extension": id_extension}
    return message_id
