import os

from app.models import OrchestrationRequest
from dotenv import load_dotenv
from requests import Response

path = current_file_directory = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(path, ".env"))


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
    def status_code(self, code: int) -> None:
        """
        Decorator for setting status_code value as a property.
        :param code: The status code to set for a service's response.
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
    def msg_content(self, content: str | dict) -> None:
        """
        Decorator for setting msg_content value as a property.
        :param content: The message content or error description to set
          as the returned value of a service's response.
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
    def should_continue(self, cont: bool) -> None:
        """
        Decorator for setting should_continue value as a property.
        :param cont: Whether the service's response merits continuing on
          to the next service.
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


def build_validation_request(
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


def build_ingestion_name_request(
    input_msg: str,
    orchestration_request: OrchestrationRequest,
    workflow_params: dict | None = None,
) -> dict:
    """
    Helper function for constructing the output payload for an API call to
    the DIBBs ingestion for the name standardization service.

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
    # Default parameter values
    default_params = {
        "trim": "true",
        "overwrite": "true",
        "case": "upper",
        "remove_numbers": "true",
    }

    # Initialize workflow_params as an empty dictionary if it's None
    workflow_params = workflow_params or {}

    for key, value in default_params.items():
        workflow_params.setdefault(key, value)

    return {
        "data": input_msg,
        "trim": workflow_params.get("trim"),
        "overwrite": workflow_params.get("overwrite"),
        "case": workflow_params.get("case"),
        "remove_numbers": workflow_params.get("remove_numbers"),
    }


def build_ingestion_phone_request(
    input_msg: str,
    orchestration_request: OrchestrationRequest,
    workflow_params: dict | None = None,
) -> dict:
    """
    Helper function for constructing the output payload for an API call to
    the DIBBs ingestion for the phone standardization service.

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
    # Since only one param, just adding explicitly
    if workflow_params is None:
        workflow_params = {"overwrite": "true"}

    return {
        "data": input_msg,
        "overwrite": workflow_params.get("overwrite"),
    }


def build_ingestion_dob_request(
    input_msg: str,
    orchestration_request: OrchestrationRequest,
    workflow_params: dict | None = None,
) -> dict:
    """
    Helper function for constructing the output payload for an API call to
    the DIBBs ingestion for the date of birth (DOB) standardization service.

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
    # Default parameter values
    default_params = {"overwrite": "true", "format": "Y%-m%-d%"}

    # Initialize workflow_params as an empty dictionary if it's None
    workflow_params = workflow_params or {}

    for key, value in default_params.items():
        workflow_params.setdefault(key, value)

    return {
        "data": input_msg,
        "overwrite": workflow_params.get("overwrite"),
        "format": workflow_params.get("format"),
    }


def build_geocoding_request(
    input_msg: str,
    orchestration_request: OrchestrationRequest,
    workflow_params: dict | None = None,
) -> dict:
    """
    Helper function for constructing the output payload for an API call to
    the DIBBs ingestion for the geocoding ingestion service.

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
    # Default parameter values
    default_params = {
        "geocode_method": "smarty",
        "smarty_auth_id": os.getenv("SMARTY_AUTH_ID"),
        "smarty_auth_token": os.getenv("SMARTY_AUTH_ID"),
        "license_type": "us-rooftop-geocoding-enterprise-cloud",
        "overwrite": "true",
    }

    # Initialize workflow_params as an empty dictionary if it's None
    workflow_params = workflow_params or {}

    for key, value in default_params.items():
        workflow_params.setdefault(key, value)

    return {
        "bundle": input_msg,
        "geocode_method": workflow_params.get("geocode_method"),
        "smarty_auth_id": workflow_params.get("smarty_auth_id"),
        "smarty_auth_token": workflow_params.get("smarty_auth_token"),
        "license_type": workflow_params.get("license_type"),
        "overwrite": workflow_params.get("overwrite"),
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
    match response.status_code:
        case 200:
            converter_response = response.json().get("response")
            fhir_msg = converter_response.get("FhirResource")
            return ServiceHandlerResponse(response.status_code, fhir_msg, True)
        case _:
            return ServiceHandlerResponse(
                response.status_code,
                f"FHIR Converter request failed: {response.text}",
                False,
            )


def unpack_parsed_message_response(
    response: Response,
) -> ServiceHandlerResponse:
    """
    Helper function for processing a response from the DIBBs message parser.
    If the status code of the response the server sent back is OK, return
    the parsed JSON message from the response body. Otherwise, report what
    went wrong based on status_code.

    :param response: The response returned by a POST request to the message parser.
    :return: A ServiceHandlerResponse with a dictionary of parsed values
      and instruction to continue, or a failed status code and error messaging.
    """
    status_code = response.status_code

    match status_code:
        case 200:
            return ServiceHandlerResponse(
                status_code, response.json().get("parsed_values"), True
            )
        case 400:
            return ServiceHandlerResponse(
                status_code, response.json().get("message"), False
            )
        case 422:
            return ServiceHandlerResponse(status_code, response.json(), False)
        case _:
            return ServiceHandlerResponse(
                status_code, f"Message Parser request failed: {response.text}", False
            )


def unpack_fhir_to_phdc_response(response: Response) -> ServiceHandlerResponse:
    """
    Helper function for processing a response from the DIBBs message parser.
    If the status code of the response the server sent back is OK, return
    the parsed XML message from the response body. Otherwise, report what
    went wrong based on status_code.

    :param response: The response returned by a POST request to the message parser.
    :return: A tuple containing the status code of the response as well as
      parsed message created by the service.
    """
    status_code = response.status_code

    match status_code:
        case 200:
            return ServiceHandlerResponse(status_code, response.content, True)
        case 422:
            return ServiceHandlerResponse(status_code, response.json(), False)
        case _:
            return ServiceHandlerResponse(
                status_code, f"Message Parser request failed: {response.text}", False
            )


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
    match response.status_code:
        case 200:
            validator_response = response.json()
            return ServiceHandlerResponse(
                response.status_code,
                validator_response.get("validation_results"),
                validator_response.get("message_valid"),
            )
        case _:
            return ServiceHandlerResponse(
                response.status_code,
                f"Validation service failed: {response.text}",
                False,
            )


def unpack_ingestion_standardization(response: Response) -> ServiceHandlerResponse:
    """
    Helper function for processing a response from the ingestion standardization
    services.
    If the status code of the response the server sent back is OK, return
    the parsed json message from the response body. Otherwise, report what
    went wrong based on status_code. Usable for DOB, name, and phone standardization,
    and geocoding.

    :param response: The response returned by a POST request to the ingestion service.
    :return: A tuple containing the status code of the response as well as
      parsed message created by the service.
    """
    status_code = response.status_code

    match status_code:
        case 200:
            return ServiceHandlerResponse(
                status_code,
                response.json().get("bundle"),
                True,
            )
        case 400:
            return ServiceHandlerResponse(
                status_code, response.json().get("message"), False
            )
        case 422:
            return ServiceHandlerResponse(status_code, response.json(), False)
        case _:
            return ServiceHandlerResponse(
                status_code,
                f"Standardization request failed: {response.text}",
                False,
            )
