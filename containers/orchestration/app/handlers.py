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


def build_message_parser_request(
    endpoint_type: str,
    orchestration_request: OrchestrationRequest,
) -> dict:
    """
    Helper function for constructing the output payload for an API call to
    the DIBBs message parser. When the user uploads data, we use the
    endpoint to determine what data to return (and what format).
    If these values cannot be determined directly from the message, the
    payload is set with default permissive EICR templates to allow the
    broadest range of conversion.

    :param endpoint_type: The endpoint of the message parser to determine
      what should be done with the FHIR bundle.
    :param orchestration_request: The request the client initially sent
      to the orchestration service. This request bundles a number of
      parameter settings into one dictionary that each handler can
      accept for consistency.
    :return: A dictionary ready to JSON-serialize as a payload to the
      message parser.
    """
    # Template will depend on input data formatting and typing
    if endpoint_type == "/parse_message":
        return {
            "message_format": "fhir",
            "parsing_schema_name": orchestration_request.get("parsing_schema_name"),
            "credential_manager": "azure",
        }
    elif endpoint_type == "/fhir_to_phdc":
        return {"phdc_report_type": "case_report"}


def unpack_message_parser_response(response: Response) -> Tuple[int, str | dict]:
    """
    Helper function for processing a response from the DIBBs message parser.
    If the status code of the response the server sent back is OK, return
    the parsed message (JSON or XML) from the response body. Otherwise, report what
    went wrong.

    :param response: The response returned by a POST request to the message parser.
    :return: A tuple containing the status code of the response as well as
      parsed message created by the service.
    """
    content_type = response.headers.get("Content-Type", "")

    # JSON-parsed messages
    if "application/json" in content_type:
        try:
            converter_response = response.json().get("response")
            status_code = converter_response.get("status_code", response.status_code)
            if status_code != 200:
                return (
                    status_code,
                    f"Message Parser request failed: {converter_response.text}",
                )
            else:
                parsed_message = converter_response.get("FhirResource")
                return (status_code, parsed_message)
        except ValueError:
            return (response.status_code, "Invalid JSON response")
    # XML-formatted messages like PHDC
    elif "application/xml" in content_type:
        try:
            # Shouldn't need to convert to str; it should already be a string:
            # https://github.com/CDCgov/phdi/blob/main/containers/message-parser/app/main.py#L157
            parsed_message = response.content
            if response.status_code != 200:
                return (
                    response.status_code,
                    f"Message Parser request failed: {converter_response.text}",
                )
            else:
                return (response.status_code, parsed_message)
        except Exception as e:
            return (response.status_code, f"XML parsing failed: {str(e)}")
