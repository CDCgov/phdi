import re

from lxml import etree

EICR_MSG_ID_XPATH = "//hl7:ClinicalDocument/hl7:id"
RR_MSG_ID_XPATH = "//hl7:ClinicalDocument/hl7:section/hl7:id"

XML_PATH_DELIMITER = "/"

ECR_NAMESPACES = {
    "hl7": "urn:hl7-org:v3",
    "xsi": "http://www.w3.org/2005/Atom",
    "cda": "urn:hl7-org:v3",
    "sdtc": "urn:hl7-org:sdtc",
    "voc": "http://www.lantanagroup.com/voc",
}


def _get_xml_message_id(id_xml_tag: etree.Element) -> dict:
    # extracts the message id from the root and extension
    # attributes from the specified xml tag and returns
    # the results in a dictionary

    if id_xml_tag == []:
        return {}
    id_root = id_xml_tag[0].get("root")
    id_extension = id_xml_tag[0].get("extension")
    message_id = {"root": id_root, "extension": id_extension}
    return message_id


def get_ecr_message_ids(parsed_ecr) -> dict:
    # get the message ids for the eicr and the rr
    xml_eicr_id = _get_xml_message_id(
        parsed_ecr.xpath(EICR_MSG_ID_XPATH, namespaces=ECR_NAMESPACES)
    )
    xml_rr_id = _get_xml_message_id(
        parsed_ecr.xpath(RR_MSG_ID_XPATH, namespaces=ECR_NAMESPACES)
    )

    return {"eicr": xml_eicr_id, "rr": xml_rr_id}


def validate_xml_elements(xml_elements, config_field) -> list:
    """
    Matches the xml_elements to the config field requirements for
    values, attributes, and relative xml element requirements for
    values, and attributes. Returns list of matching fields.

    :param xml_elements: A list of xml elements
    :param config_field: A dictionary of the requirements of the field.
    :return: A list of matched xml elemnts
    """
    if not xml_elements:
        return []
    validated_elements = []
    for xml_element in xml_elements:
        if not _validate_xml_relatives(xml_element, config_field):
            continue
        found = _check_xml_names_and_attribs_exist(xml_element, config_field)
        if found:
            validated_elements.append(xml_element)
    return validated_elements


def _validate_xml_relatives(xml_element, config_field) -> bool:
    """
    Gets the 'relatives' portion of the configuration for a particular
    field and validates that the required attributes and values in the
    relative xml paths are present.

    :param xml_element: The key xml element that is being evaluated as
        well as its relative xml elements.
    :param config_field: A dictionary of the requirements for validating
        the key xml elements relative xml elements.
    :return: Bool - True if all relative xml elements match the criteria
        specified in the configuration, otherwise false.
    """
    relatives_valid = True
    relatives = config_field.get("relatives")
    if relatives is None:
        return relatives_valid
    for relative_config in relatives:
        base_cda_path = config_field.get("cdaPath")
        if (
            _validate_xml_related_element(
                xml_element=xml_element,
                cda_path=base_cda_path,
                relative_config=relative_config,
            )
            is None
        ):
            relatives_valid = False
    return relatives_valid


def _check_xml_names_and_attribs_exist(xml_element, config_field) -> bool:
    """
    Confirms that the xml element name and attributes specified in
    the configuration actually exist.

    :param xml_element: The key xml element that is being evaluated.
    :param config_field: A dictionary of the requirements for validating
        the key xml elements name and attributes
    :return: Bool - True if the name and attributes exist in the passed in
        xml element, otherwise false.
    """
    # If the configuration specified field name doesn't match the xml elements
    # tag name, then return false to go to the next xml element
    field_name = re.search(r"(?!\:)[a-zA-z]+\w$", config_field.get("cdaPath")).group(0)

    if field_name.lower() not in xml_element.tag.lower():
        return False

    # Don't try to evaluate matches for the xml element's attributes
    # if we are validating all fields as indicated in the configuration
    # for the field/xml element
    match_attributes = False if config_field.get("validateAll") == "True" else True
    if not match_attributes:
        return True

    # Check if the xml element passed in has the right attributes
    #  and if the values of the attribute correspond to the
    #  requirements in the configuration
    field_attributes = config_field.get("attributes")
    if field_attributes:
        for attribute in field_attributes:
            # If field is supposed to have an attribute and doesn't,
            # return that the field has failed validation for that
            # attribute.
            if not xml_element.get(attribute.get("attributeName")):
                return False
    else:
        # If there are not specified attributes to validate within the
        # configuration, but there are attributes in the xml element
        # then return a False/Fail
        # TODO: is this how this should be working??
        if xml_element.attrib:
            return False
    return True


def _validate_xml_related_element(xml_element, cda_path, relative_config) -> str:
    """
    Validates a related xml element, to the key xml element,
    against the configured rules for the related element's
    location to the key element and the existence of values
    and attributes for the related xml element.  If the relative
    xml element meets all the configured criteria, then the xml
    element will be returned, otherwise None.

    :param xml_element: The key xml element.
    :param cda_path: A string representing the location of the key xml element.
    :param config_field: A dictionary of the requirements for the related xml element.
    :return: A related xml element if the related xml element meets the configured
        criteria, otherwise return None.
    """
    if xml_element is None:
        return None
    relative_cda_path = relative_config.get("cdaPath")
    relative_tag_name = re.search(
        r"(?!\:)[a-zA-z]+\w$", relative_config.get("cdaPath")
    ).group(0)

    xml_iterator = _get_xml_relative_iterator(cda_path, relative_cda_path, xml_element)

    # if there are no related xml elements based upon the
    # specified cda paths then just return None
    if xml_iterator is None or len(xml_iterator) == 0:
        return None

    # sibling, descendant, child iterators
    # are of different type than ancestors
    # It's not clear why, but this prevents errors
    # and ensures that we have the correct element tag
    # and related element
    try:
        related_xml_element_tag = xml_iterator.tag
        related_xml_element = xml_iterator
    except Exception as e:
        print(e)
        related_xml_element = None
        related_xml_element_tag = None

    for xi in xml_iterator:
        # loop through iterator - unless it's
        # a ancestor - if that is the case then
        # the iterator itself IS the proper related
        # element and we want to use that - otherwise
        # loop through the list of elements in the list
        if related_xml_element_tag is None:
            related_xml_element = xi
            related_xml_element_tag = related_xml_element.tag

        if relative_tag_name in related_xml_element_tag:
            relative_validated = _check_xml_names_and_attribs_exist(
                xml_element=related_xml_element, config_field=relative_config
            )
            relative_attributes_validated = validate_xml_attributes(
                related_xml_element, relative_config
            )

            if not relative_validated or len(relative_attributes_validated) != 0:
                return None
            else:
                return related_xml_element
        else:
            related_xml_element = None
            related_xml_element_tag = None


def _get_xml_relative_iterator(cda_path, relative_cda_path, xml_element) -> list:
    """
    Gets an iterator, basically a list of xml elements, based on the key
    xml element's path and the relative xml element's path being
    searched for.

    :param cda_path: A string representing the location of the key xml element.
    :param relative_cda_path: A string representing the path of the relative
        xml element to be searched for.
    :param xml_element: The key xml element.
    :return: An lxml defined iterator of the relative xml elements
        based on the key xml element.
    """
    if xml_element is None:
        return None
    # get the difference of the number of '/' between the key cda_path and the
    # relative_cda_path
    diff = len(cda_path.split(XML_PATH_DELIMITER)) - len(
        relative_cda_path.split(XML_PATH_DELIMITER)
    )
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
    # element is an acestor to the main element
    elif diff > 0:
        # get all the ancestors and put them into a list
        # and then get the one that is at the level
        # equal to the diff -1 (to account for array numbering)

        if len(list(xml_element.iterancestors())) < diff - 1:
            return None
        xml_relative_element = list(xml_element.iterancestors())[diff - 1]
        return xml_relative_element
    # element is a child of the main element
    elif diff == -1:
        return list(xml_element.iterchildren())
    # if diff is < -1 then it's a descendant and it's
    # going to have to return all tags under the base
    # xml element
    else:
        return list(xml_element.iterdescendants())


def validate_xml_attributes(xml_element, config_field) -> list:
    """
    Validates an xml element by checking if the configured attribute(s) exist
    and match the configured regex pattern for the value of the attribute.
    If the xml element, and it's subsequent attribute(s), do not pass the checks,
    based upon what is in the configuration, then an error message is added to
    the validation results.

    :param xml_element: The xml element that will have its attributes validated.
    :param config_field: A dictionary that contains the configuration that
        specifies what the attribute(s) for the xml element should be named
        and how the values should be patterned.
    :return: A list of errors or an empty list.  If the list is empty then
        the validation was successful.
    """
    config_attribs = config_field.get("attributes")
    if not config_attribs:
        return []

    error_messages = []
    for attribute in config_attribs:
        if "attributeName" in attribute:
            attribute_name = attribute.get("attributeName")
            attribute_value = xml_element.get(attribute_name)
            if not attribute_value:
                message = _get_ecr_custom_message(
                    config_field,
                    f"Could not find attribute '{attribute_name}'. "
                    + f"{get_xml_element_details(xml_element, config_field)}",
                )
                error_messages.append(message)
        if "regEx" in attribute:
            pattern = re.compile(attribute.get("regEx"))
            if (not attribute_value) or (not pattern.match(attribute_value)):
                message = _get_ecr_custom_message(
                    config_field,
                    f"Attribute: '{attribute_name}'"
                    + " not in expected format. "
                    + f"{get_xml_element_details(xml_element, config_field)}",
                )
                error_messages.append(message)
    return error_messages


def _get_ecr_custom_message(config_field, default_message):
    message = default_message
    if config_field.get("customMessage"):
        message = config_field.get("customMessage")
    return message


def get_xml_element_details(xml_element, config_field) -> str:
    """
    Gets the name, value, of the xml element referenced as well
    as the details of any configured relative xml elements for
    the referenced xml element and formats this information into
    a single string for use in the validation messages.

    :param xml_element: The key xml element.
    :param config_field: A dictionary of the configured requirements
        for the xml element.
    :return: A single string containing the information about the
        key xml element and its attribute(s).
    """
    if config_field is None or config_field == {}:
        return ""
    name = [f"Field name: '{config_field.get('fieldName')}'"]
    config_attributes = config_field.get("attributes")
    attributes = (
        ["Attributes:"] + _get_xml_attributes(xml_element, config_attributes)
        if config_attributes
        else []
    )
    relative_string = _get_xml_relatives_details(config_field.get("relatives"))
    value = (
        [f"value: '{''.join(xml_element.itertext())}'"]
        if (
            config_field.get("textRequired")
            and xml_element is not None
            and "".join(xml_element.itertext()) != ""
        )
        else []
    )
    return " ".join(name + value + attributes + relative_string)


def _get_xml_relatives_details(relatives_config: dict) -> list:
    """
    Gets the name and configured attribute information for
    any relative xml elements based upon the relative config
    section passed in and formats this information into
    a single string for use in the validation messages.

    :param relatives_config: A dictionary of the configured requirements
        for the relative xml element.
    :return: A single string, in a list, containing the information about the
        relative xml element and its attribute(s).
    """
    relative_string = []
    if relatives_config:
        relative_string.append("Related elements:")
        for rel_config in relatives_config:
            relative_field_name = rel_config.get("name")
            relative_name = (
                ["Field name: '" + relative_field_name + "'"]
                if relative_field_name
                else []
            )
            config_related_attributes = rel_config.get("attributes")
            relative_attributes = (
                ["Attributes:"] + _get_xml_attributes(None, config_related_attributes)
                if config_related_attributes
                else []
            )
            relative_string += relative_name
            relative_string += relative_attributes
    return relative_string


def _get_xml_attributes(xml_element, config_attributes) -> list:
    """
    Takes the xml element, along with its configuration to create
    a list of strings that include attribute name, required
    patterns, and the actual value of said attribute.

    :param xml_element: The key xml element.
    :param config_attributes: A dictionary of the configured requirements
        for the attributes for the key xml element.
    :return: A single string containing the information about the
        key xml elements attribute(s).
    """
    attrs = []
    if config_attributes is None or config_attributes == "":
        return attrs
    for attribute in config_attributes:
        attr_index = len(attrs) + 1
        attribute_name = attribute.get("attributeName")
        reg_ex = attribute.get("regEx")
        reg_ex_string = (
            f" with the required value pattern: '{reg_ex}'" if reg_ex else ""
        )

        if xml_element is not None and xml_element.get(attribute_name):
            attribute_value = f" actual value: '{xml_element.get(attribute_name)}'"
        else:
            attribute_value = ""

        attrs.append(
            f"attribute #{attr_index}: "
            + f"'{attribute_name}'{reg_ex_string}{attribute_value}"
        )
    return [", ".join(attrs)]


def validate_xml_value(xml_element, config_field) -> list:
    """
    Validates the value of an xml element (ie... between the tags) based upon
    validating the xml element exists within the relative xml element location
    based upon the configuration of the parent of the xml element.
    Then it validates that the value of xml element matches the value pattern
    listed in the config.

    :param xml_element: The key xml element being evaluated.
    :param config_field: A dictionary that contains the configuration information
        necessary to validate the location and value of the key xml element
    :return: A list of error messages if validation fails, otherwise an
        empty list.
    """
    # If value for xml element is not required return empty list
    if not config_field.get("textRequired"):
        return []

    value = "".join(xml_element.itertext())
    config_regex = config_field.get("regEx")
    # first check if the value matches the regex from the config
    if config_regex is not None:
        pattern = re.compile(config_regex)
        if pattern.match(value) is None:
            message = _get_ecr_custom_message(
                config_field,
                "The field value does not exist or "
                + "doesn't match the following pattern: '"
                + config_regex
                + f"'. For the {get_xml_element_details(xml_element, config_field)}",
            )
            return [message]
        else:
            return []
    # otherwise just verify that a value is present
    else:
        if value is not None and value != "":
            return []
        else:
            message = _get_ecr_custom_message(
                config_field,
                "Field does not have a value. "
                + f"{get_xml_element_details(xml_element, config_field)}",
            )
            return [message]
