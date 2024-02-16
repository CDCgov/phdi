from typing import Tuple

from app.models import OrchestrationRequest
from requests import Response


MESSAGE_TO_TEMPLATE_MAP = {
    "fhir": "",
    "ecr": "EICR",
    "elr": "ORU_R01",
    "vxu": "VXU_V04",
}


def build_fhir_converter_request(
    input_msg: str, orchestration_request: OrchestrationRequest
) -> dict:
    """
    Helper function for constructing the input payload for an API call to
    the DIBBs FHIR converter. When the user uploads data, we use the
    properties of the uploaded message to determine the appropriate
    conversion settings (such as the root template or HL7v2 basis segment).
    If these values cannot be determined directly from the message, the
    payload is set with default permissive EICR templates to allow the
    broadest range of conversion.

    :param input_msg: The data the user sent for workflow processing, as
      a string.
    :param orchestration_request: The request the client initially sent
      to the orchestration service. This request bundles a number of
      parameter settings into one dictionary that each handler can
      accept for consistency.
    :return: A dictionary ready to JSON-serialize as a payload to the
      FHIR converter.
    """
    # Template will depend on input data formatting and typing
    input_type = orchestration_request.get("message_type")
    root_template = MESSAGE_TO_TEMPLATE_MAP[input_type]
    return {
        "input_data": input_msg,
        "input_type": input_type,
        "root_template": root_template,
        "rr_data": orchestration_request.get("rr_data"),
    }


def unpack_fhir_converter_response(response: Response) -> Tuple[int, str | dict]:
    """
    Helper function for processing a response from the DIBBs FHIR converter.
    If the status code of the response the server sent back is OK, return
    the parsed FHIR bundle from the response body. Otherwise, report what
    went wrong.

    :param response: The response returned by a POST request to the FHIR
      converter.
    :return: A tuple containing the status code of the response as well as
      the FHIR bundle that the service generated.
    """
    converter_response = response.json().get("response")
    if converter_response.status_code != 200:
        return (
            converter_response.status_code,
            f"FHIR Converter request failed: {converter_response.text}",
        )
    else:
        fhir_msg = converter_response.get("FhirResource")
        return (converter_response.status_code, fhir_msg)


def build_message_parser_message_request(
    input_msg: str,
    orchestration_request: OrchestrationRequest,
    workflow_params: dict | None = None,
) -> dict:
    """
    Helper function for constructing the output payload for an API call to
    the DIBBs message parser for JSON messages.

    :param input_msg: The data the user sent for workflow processing, as
      a string.
    :param orchestration_request: The request the client initially sent
      to the orchestration service. This request bundles a number of
      parameter settings into one dictionary that each handler can
      accept for consistency.
    :param workflow_params: Optionally, a set of configuration parameters
      included in the workflow config for the converter step of a workflow.
    :return: A dictionary ready to JSON-serialize as a payload to the
      message parser.
    """
    # Template will depend on input data formatting and typing
    return {
        "message": input_msg,
        "message_format": orchestration_request.get("message_type"),
        "parsing_schema_name": workflow_params.get("parsing_schema_name"),
        "credential_manager": workflow_params.get("credential_manager"),
    }


def build_message_parser_phdc_request(
    input_msg: str,
    orchestration_request: OrchestrationRequest,
    workflow_params: dict | None = None,
) -> dict:
    """
    Helper function for constructing the output payload for an API call to
    the DIBBs message parser for PHDC-formatted XML.

    :param input_msg: The data the user sent for workflow processing, as
      a string.
    :param orchestration_request: The request the client initially sent
      to the orchestration service. This request bundles a number of
      parameter settings into one dictionary that each handler can
      accept for consistency.
    :param workflow_params: Optionally, a set of configuration parameters
      included in the workflow config for the converter step of a workflow.
    :return: A dictionary ready to JSON-serialize as a payload to the
      message parser.
    """

    return {
        "message": input_msg,
        "phdc_report_type": workflow_params.get("phdc_report_type"),
    }


def unpack_message_parser_message_response(
    response: Response,
) -> Tuple[int, str | dict]:
    """
    Helper function for processing a response from the DIBBs message parser.
    If the status code of the response the server sent back is OK, return
    the parsed JSON message from the response body. Otherwise, report what
    went wrong.

    :param response: The response returned by a POST request to the message parser.
    :return: A tuple containing the status code of the response as well as
      parsed message created by the service.
    """
    try:
        converter_response = response.json()
        status_code = converter_response.get("status_code", response.status_code)
        if status_code != 200:
            error_message = response.text
            return (
                status_code,
                f"Message Parser request failed: {error_message}",
            )
        else:
            parsed_message = converter_response.get("parsed_values")
            return (status_code, parsed_message)
    except ValueError:
        return (response.status_code, "Invalid JSON response")


def unpack_message_parser_phdc_response(response: Response) -> Tuple[int, str | dict]:
    """
    Helper function for processing a response from the DIBBs message parser.
    If the status code of the response the server sent back is OK, return
    the parsed XML message from the response body. Otherwise, report what
    went wrong.

    :param response: The response returned by a POST request to the message parser.
    :return: A tuple containing the status code of the response as well as
      parsed message created by the service.
    """
    # XML-formatted messages like PHDC
    try:
        if response.status_code != 200:
            error_message = response.text
            return (response.status_code, error_message)
        else:
            # XML response handling
            parsed_message = response.content
            return (response.status_code, parsed_message)
    except Exception as e:
        return (response.status_code, f"XML parsing failed: {str(e)}")
