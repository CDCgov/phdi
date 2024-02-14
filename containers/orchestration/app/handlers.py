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
    parameters of their request to assign an appropriate root conversion
    template and pass this information to the conversion service.

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


def build_valiation_request(
    input_msg: str, orchestration_request: OrchestrationRequest
) -> dict:
    """
    Helper function for constructing the input payload for an API call to
    the DIBBs validation service. This handler simply reorders and formats
    the parameters into an acceptable input for the validator.

    :param input_msg: The data the user sent for workflow processing, as
      a string.
    :param orchestration_request: The request the client initially sent
      to the orchestration service. This request bundles a number of
      parameter settings into one dictionary that each handler can
      accept for consistency.
    :return: A dictionary ready to send to the validation service.
    """
    return {
        "message_type": orchestration_request.get("message_type"),
        "include_error_types": orchestration_request.get("include_error_types"),
        "message": orchestration_request.get("message"),
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
            f"FHIR Converter request failed: {response.text}",
        )
    else:
        fhir_msg = converter_response.get("FhirResource")
        return (converter_response.status_code, fhir_msg)


def unpack_validation_response(response: Response) -> Tuple[int, str | bool | dict]:
    """
    Helper function for processing a response from the DIBBs validation
    service. If the message is valid, with no errors in data structure,
    just report that to the calling orchestrator so we can continue the
    workflow. If the message isn't valid but the service succeeded (status
    code 200), tell the caller what the errors were so they can abort
    and inform the user.

    :param response: The response returned by a POST request to the validation
      service.
    :return: A tuple containing the status code of the response as well as
      either a `True` boolean if the message is valid, or a dictionary of
      errors if it isn't.
    """
    validator_response = response.json()
    if validator_response.status_code != 200:
        return (
            validator_response.status_code,
            f"Validation service failed: {response.text}",
        )

    # TODO: When we re-write the call apis loop, we should have a special case
    # at the top of the function, before getting into the loop, that does
    # validation service requests and response handling. This is because
    # the validation service is the only endpoint that _does not_ also return
    # message data to the caller. The response object contains only whether
    # the message is valid and what kinds of errors may or may not have
    # happened. So, the move in call_apis will be to check if the first step
    # is validation, and if yes, make a separate validate request. If the
    # response comes back 200 with no errors, then we move into the rest of
    # the loop, but if it doesn't (and the workflow inlcuded validation),
    # then we abort and report the data invalidity to the user.
    else:
        if validator_response.get("message_valid") is True:
            return (
                validator_response.status_code,
                validator_response.get("message_valid"),
            )
        else:
            return (
                validator_response.status_code,
                validator_response.get("validation_results"),
            )
