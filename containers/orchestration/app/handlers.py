from app.models import OrchestrationRequest
from requests import Response


MESSAGE_TO_TEMPLATE_MAP = {
    "fhir": "",
    "ecr": "EICR",
    "elr": "ORU_R01",
    "vxu": "VXU_V04",
}


class ServiceHandlerResponse:
    """
    Wrapper class that encapsulates all the information the `call_apis`
    function needs to handle processing one service's output as another
    service's input. This class captures the return status of a service
    (status code), what data it sent back (its message content), and
    whether this data is fit for processing by another service (whether
    call_apis should continue). Some of the DIBBs services either do not
    return altered data to the caller, or return a 200 status code but
    still flag an error with their input, so capturing these nuances
    allows `call_apis` to be completely agnostic about the response
    content a service sends back.
    """

    def __init__(
        self, status_code: int, msg_content: str | dict, should_continue: bool
    ):
        self._status_code = status_code
        self._msg_content = msg_content
        self._should_continue = should_continue

    @property
    def status_code(self) -> int:
        """
        The status code the service returned to the caller.
        """
        return self._status_code

    @status_code.setter
    def status_code(self, code) -> None:
        """
        Decorator for setting status_code value as a property.
        """
        self._status_code = code

    @property
    def msg_content(self) -> str | dict:
        """
        The data the service sent back to the caller. If this is a
        transformation or standardization service, this value holds
        the altered and updated data the service computed. If this
        is the validation or a verification service, this value
        holds any errors the service flagged in its input.
        """
        return self._msg_content

    @msg_content.setter
    def msg_content(self, content) -> None:
        """
        Decorator for setting msg_content value as a property.
        """
        self._msg_content = content

    @property
    def should_continue(self) -> bool:
        """
        Whether the calling function can hand the processed data off
        to the next service, based on the current service's status
        and message content validity.
        """
        return self._should_continue

    @should_continue.setter
    def should_continue(self, cont) -> None:
        """
        Decorator for setting should_continue value as a property.
        """
        self._should_continue = cont


def build_fhir_converter_request(
    input_msg: str,
    orchestration_request: OrchestrationRequest,
    workflow_params: dict | None = None,
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
    :param workflow_params: Optionally, a set of configuration parameters
      included in the workflow config for the converter step of a workflow.
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
    input_msg: str,
    orchestration_request: OrchestrationRequest,
    workflow_params: dict | None = None,
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
    :param workflow_params: Optionally, a set of configuration parameters
      included in the workflow config for the validation step of a workflow.
    :return: A dictionary ready to send to the validation service.
    """
    return {
        "message_type": orchestration_request.get("message_type"),
        "include_error_types": workflow_params.get("include_error_types"),
        "message": orchestration_request.get("message"),
        "rr_data": orchestration_request.get("rr_data"),
    }


def unpack_fhir_converter_response(response: Response) -> ServiceHandlerResponse:
    """
    Helper function for processing a response from the DIBBs FHIR converter.
    If the status code of the response the server sent back is OK, return
    the parsed FHIR bundle from the response body. Otherwise, report what
    went wrong.

    :param response: The response returned by a POST request to the FHIR
      converter.
    :return: A ServiceHandlerResponse with a FHIR bundle and instruction
      to continue, or a failed status code and error messaging.
    """
    converter_response = response.json().get("response")
    if converter_response.status_code != 200:
        return ServiceHandlerResponse(
            converter_response.status_code,
            f"FHIR Converter request failed: {response.text}",
            False,
        )
    else:
        fhir_msg = converter_response.get("FhirResource")
        return ServiceHandlerResponse(converter_response.status_code, fhir_msg, True)


def unpack_validation_response(response: Response) -> ServiceHandlerResponse:
    """
    Helper function for processing a response from the DIBBs validation
    service. If the message is valid, with no errors in data structure,
    just report that to the calling orchestrator so we can continue the
    workflow. If the message isn't valid but the service succeeded (status
    code 200), tell the caller what the errors were so they can abort
    and inform the user.

    :param response: The response returned by a POST request to the validation
      service.
    :return: A ServiceHandlerResponse with any validation errors the data
      generated, or an instruction to continue to the next service.
    """
    validator_response = response.json()
    if validator_response.status_code != 200:
        return ServiceHandlerResponse(
            validator_response.status_code,
            f"Validation service failed: {response.text}",
            False,
        )
    else:
        return ServiceHandlerResponse(
            validator_response.status_code,
            validator_response.get("validation_results"),
            validator_response.get("message_valid"),
        )
