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
    Helper functoin for processing a response from the DIBBs FHIR converter.
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
        return (converter_response.status_code, "Bad Request: FHIR Conversion failed.")
    else:
        fhir_msg = converter_response.get("FhirResource")
        return (converter_response.status_code, fhir_msg)
