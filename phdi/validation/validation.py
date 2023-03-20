from lxml import etree
from xml_utils import (
    get_ecr_message_ids,
    _validate_xml_elements,
    _validate_xml_attributes,
    _validate_xml_value,
    _get_xml_element_details,
    ECR_NAMESPACES,
)


ERROR_MESSAGES = {
    "fatal": [],
    "errors": [],
    "warnings": [],
    "information": [],
    "message_ids": {},
}


def validate_ecr(ecr_message: str, config: dict, include_error_types: list) -> dict:
    """
    Receives an ecr message (a combined RR and eICR), a configuration of
    what fields are to be validated and how they are to be validated, as
    well as a list of error message types to include (default is all fatal
    errors, basic errors, warnings, and information).  The result of
    validation is returned in a dictionary that also contains a boolean
    if the ecr message is valid or not.

    :param ecr_message: A eCR message that contains both eICR and RR fields.
    :param config: A dictionary of the requirements for validation of the
      eCR message.
    :param include_error_types: A list of error message types to include
        in the final validation response.  Default (fatal, errors,
        warnings, information)
    :return: A dictionary containing bool message_valid as well as a
        dictionary containing the validation results/errors.
    """
    # encoding ecr_message to allow it to be
    #  parsed and organized as an lxml Element Tree Object
    xml = ecr_message.encode("utf-8")
    parser = etree.XMLParser(ns_clean=True, recover=True, encoding="utf-8")

    # we need a try-catch around this to ensure that the ecr message
    # passed in is proper XML - also ensure it's a clinical document
    try:
        parsed_ecr = etree.fromstring(xml, parser=parser)
        parsed_ecr.xpath("//hl7:ClinicalDocument", namespaces=ECR_NAMESPACES)

    except AttributeError:
        _add_basic_error("eCR Message is not valid XML!")
        return _response_builder(include_error_types=include_error_types)

    _add_message_ids(message_ids=get_ecr_message_ids(parsed_ecr=parsed_ecr))

    for field in config.get("fields"):
        # extract the specific information from the configuration
        # for the different fields
        cda_path = field.get("cdaPath")
        # get a list of XML elements that match the field configuration
        matched_xml_elements = _validate_xml_elements(
            xml_elements=parsed_ecr.xpath(cda_path, namespaces=ECR_NAMESPACES),
            config_field=field,
        )
        error_message_type = (
            field.get("errorType")
            if field.get("errorType") in ERROR_MESSAGES.keys()
            else "errors"
        )
        # if there are no xml elements that were valid for
        # the configuration then store an error for that based
        # upon the configured error message type
        if not matched_xml_elements:
            error_message = "Could not find field. " + _get_xml_element_details(
                None, field
            )
            _append_error_message(
                error_message_type=error_message_type, message=error_message
            )
            continue
        # continue the validation steps for xml attributes and values
        attribute_errors = []
        value_errors = []
        for xml_element in matched_xml_elements:
            attribute_errors += _validate_xml_attributes(xml_element, field)
            value_errors += _validate_xml_value(xml_element, field)
        # this handles a specific case where just ONE xml element
        # must meet the attribute or xml value criteria - otherwise
        # you wil want to include an error.
        if not (
            field.get("validateOne")
            and len(attribute_errors) < len(matched_xml_elements)
            and len(value_errors) < len(matched_xml_elements)
        ):
            for attribute_error in attribute_errors:
                _append_error_message(
                    error_message_type=error_message_type, message=attribute_error
                )
            for value_error in value_errors:
                _append_error_message(
                    error_message_type=error_message_type, message=value_error
                )
    response = _response_builder(include_error_types=include_error_types)
    return response


def _organize_error_messages(include_error_types: list):
    # utilize the error_types to filter out the different error message
    # types as well as specify the difference between the different error types
    # during the validation process

    # fatal warnings cannot be filtered and will be automatically included!

    filtered_errors = (
        ERROR_MESSAGES["errors"] if "errors" in include_error_types else []
    )
    filtered_warnings = (
        ERROR_MESSAGES["warnings"] if "warnings" in include_error_types else []
    )
    filtered_information = (
        ERROR_MESSAGES["information"]
        if "information" in include_error_types else []
    )

    ERROR_MESSAGES["errors"] = filtered_errors
    ERROR_MESSAGES["warnings"] = filtered_warnings
    ERROR_MESSAGES["information"] = filtered_information


def _response_builder(include_error_types: list) -> dict:
    if ERROR_MESSAGES.get("fatal") != []:
        valid = False
    else:
        valid = True
        _add_information_message("Validation completed with no fatal errors!")

    return {
        "message_valid": valid,
        "validation_results": _organize_error_messages(
            include_error_types=include_error_types
        ),
    }


def _append_error_message(error_message_type: str, message: str):
    if error_message_type == "fatal":
        _add_fatal_error(message=message)
    if error_message_type == "errors":
        _add_basic_error(message=message)
    if error_message_type == "warnings":
        _add_warning_message(message=message)
    if error_message_type == "information":
        _add_information_message(message=message)


def _add_fatal_error(message: str):
    if message is not None and message != "":
        ERROR_MESSAGES["fatal"].append(message)


def _add_basic_error(message: str):
    if message is not None and message != "":
        ERROR_MESSAGES["errors"].append(message)


def _add_warning_message(message: str):
    if message is not None and message != "":
        ERROR_MESSAGES["warnings"].append(message)


def _add_information_message(message: str):
    if message is not None and message != "":
        ERROR_MESSAGES["information"].append(message)


def _add_message_ids(message_ids: dict):
    if message_ids is not None and len(message_ids) > 0:
        ERROR_MESSAGES[message_ids] = message_ids
