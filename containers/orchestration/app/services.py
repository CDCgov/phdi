import json
import os

import requests
from fastapi import HTTPException
from fastapi import Response
from fastapi import WebSocket
from opentelemetry import trace
from opentelemetry.trace.status import StatusCode

from app.handlers.request_builders.ecr_viewer import build_save_fhir_data_body
from app.handlers.request_builders.fhir_converter import build_fhir_converter_request
from app.handlers.request_builders.ingestion import build_geocoding_request
from app.handlers.request_builders.ingestion import build_ingestion_dob_request
from app.handlers.request_builders.ingestion import build_ingestion_name_request
from app.handlers.request_builders.ingestion import build_ingestion_phone_request
from app.handlers.request_builders.ingestion import build_validation_request
from app.handlers.request_builders.message_parser import (
    build_message_parser_message_request,
)
from app.handlers.request_builders.message_parser import (
    build_message_parser_phdc_request,
)
from app.handlers.request_builders.trigger_code_reference import (
    build_stamp_condition_extensions_request,
)
from app.handlers.response_builders.ecr_viewer import unpack_save_fhir_data_response
from app.handlers.response_builders.fhir_converter import unpack_fhir_converter_response
from app.handlers.response_builders.ingestion import unpack_ingestion_standardization
from app.handlers.response_builders.ingestion import unpack_validation_response
from app.handlers.response_builders.message_parser import unpack_fhir_to_phdc_response
from app.handlers.response_builders.message_parser import unpack_parsed_message_response
from app.handlers.response_builders.trigger_code_reference import (
    unpack_stamp_condition_extensions_response,
)
from app.handlers.ServiceHandlerResponse import ServiceHandlerResponse
from app.models import OrchestrationRequest
from app.utils import format_service_url

# Integrate services tracer with automatic instrumentation context
tracer = trace.get_tracer("orchestration_services.py_tracer")

# Locations of the various services the service will delegate
SERVICE_URLS = {
    "validation": os.environ.get("VALIDATION_URL"),
    "ingestion": os.environ.get("INGESTION_URL"),
    "fhir_converter": os.environ.get("FHIR_CONVERTER_URL"),
    "message_parser": os.environ.get("MESSAGE_PARSER_URL"),
    "trigger_code_reference": os.environ.get("TRIGGER_CODE_REFERENCE_URL"),
    "save_bundle": os.environ.get("ECR_VIEWER_URL"),
    "save_metadata": os.environ.get("ECR_VIEWER_URL"),
}

# Mappings of endpoint names to the service input and output building
# functions--lets the workflow config drive the API loop with no need
# to change function signatures
ENDPOINT_TO_REQUEST_BODY = {
    "validate": build_validation_request,
    "convert-to-fhir": build_fhir_converter_request,
    "geocode_bundle": build_geocoding_request,
    "standardize_names": build_ingestion_name_request,
    "standardize_dob": build_ingestion_dob_request,
    "standardize_phones": build_ingestion_phone_request,
    "stamp-condition-extensions": build_stamp_condition_extensions_request,
    "parse_message": build_message_parser_message_request,
    "fhir_to_phdc": build_message_parser_phdc_request,
    "save-fhir-data": build_save_fhir_data_body,
}
ENDPOINT_TO_RESPONSE = {
    "validate": unpack_validation_response,
    "convert-to-fhir": unpack_fhir_converter_response,
    "geocode_bundle": unpack_ingestion_standardization,
    "standardize_names": unpack_ingestion_standardization,
    "standardize_dob": unpack_ingestion_standardization,
    "standardize_phones": unpack_ingestion_standardization,
    "stamp-condition-extensions": unpack_stamp_condition_extensions_response,
    "parse_message": unpack_parsed_message_response,
    "fhir_to_phdc": unpack_fhir_to_phdc_response,
    "save-fhir-data": unpack_save_fhir_data_response,
}


def post_request(url: str, payload: dict) -> Response:
    """
    Helper function to post an API request to a particular endpoint using
    the `requests` module.

    :param url: The full URL of the endpoint to-hit.
    :param payload: The body of the Request object, as a dictionary.
    :return: A Response object from the posted endpoint.
    """
    return requests.post(url, json=payload)


async def _send_websocket_dump(
    endpoint_name: str,
    base_response: Response,
    service_response: ServiceHandlerResponse,
    progress_dict: dict,
    websocket: WebSocket,
) -> dict:
    """
    Helper method that sends service response information from a DIBBs
    API call to a particular web socket.

    :param endpoint_name: Name of the endpoint to inform the websocket of.
    :param base_response: The unaltered response the service sent back.
    :param service_response: The unpacked handler response with logic
      applied determining whether the calling function should continue.
    :param progress_dict: The dictionary tracking progres to notify the
      websocket of.
    :param websocket: The websocket to stream the data to.
    :return: The updated progress dictionary.
    """
    with tracer.start_as_current_span(
        "send_websocket_dump_to_progress_dict",
        kind=trace.SpanKind(0),
        attributes={
            "endpoint_name": endpoint_name,
            "socket_client_status": websocket.client_state,
            "socket_server_status": websocket.application_state,
        },
    ) as dump_span:
        status = (
            "success"
            if (
                service_response.status_code == 200 and service_response.should_continue
            )
            else "error"
        )

        dump_span.add_event(
            "determining success logic, preparing to write to progress dict",
            attributes={"status": status, "status_code": base_response.status_code},
        )

        # Write service responses into websocket message
        progress_dict[endpoint_name] = {
            "status": status,
            "status_code": base_response.status_code,
            "response": base_response.json(),
        }

        dump_span.add_event("dumping JSON to socket's text receiver")
        await websocket.send_text(json.dumps(progress_dict))
        return progress_dict


async def call_apis(
    config: dict, input: OrchestrationRequest, websocket: WebSocket = None
) -> tuple:
    """
    Asynchronous function that loops over each step in a provided workflow
    config and performs each service step. The function builds a request
    packet for each step, posts to the appropriate API, then unpacks the
    service response. If the response is valid and has data, it is passed
    to the next service as input. If the response was unsuccessful, the
    function communicates errors to the caller.

    :param config: The config-driven workflow extracted from a JSON file.
    :param input: The original request to the orchestration service.
    :param websocket: Optionally, a socket to which to stream input
      bytes on the service's progress and results.
    :return: A tuple holding the concluding status code of the orchestration
      service, as well as each step's response along the way.
    """
    with tracer.start_as_current_span(
        "call-apis",
        kind=trace.SpanKind(0),
        attributes={
            "config": config,
            "message_type": input.get("message_type"),
            "data_type": input.get("data_type"),
        },
    ) as call_span:
        call_span.add_event("unpacking input parameters")
        workflow = config.get("workflow", [])
        current_message = input.get("message")
        response = current_message
        responses = {}
        # For websocket json dumps
        progress_dict = {}
        for step in workflow:
            service = step["service"]
            endpoint = step["endpoint"]
            endpoint_name = endpoint.split("/")[-1]
            params = step.get("params", {})
            previous_response_to_param_mapping = step.get(
                "previous_response_to_param_mapping", None
            )
            call_span.add_event(
                "formatting parameters for service " + service,
                attributes={
                    "service": service,
                    "endpoint": endpoint,
                    "endpoint_name": endpoint_name,
                    "config_params": _param_dict_to_str(params),
                    "previous_response_to_param_mapping": _param_dict_to_str(
                        previous_response_to_param_mapping
                    ),
                },
            )

            service_url = format_service_url(SERVICE_URLS[service], endpoint)

            request_body_func = ENDPOINT_TO_REQUEST_BODY[endpoint_name]
            response_func = ENDPOINT_TO_RESPONSE[endpoint_name]
            call_span.add_event(
                "packaging data to building block handler",
                attributes={
                    "request_body_handler": request_body_func.__str__(),
                    "response_extraction_handler": response_func.__str__(),
                },
            )

            if previous_response_to_param_mapping:
                for k, v in previous_response_to_param_mapping.items():
                    params[v] = responses[k]
            request_body = request_body_func(current_message, input, params)
            call_span.add_event("posting to `service_url` " + service_url)
            response = post_request(service_url, request_body)
            call_span.add_event("response received from building block")
            service_response = response_func(response)

            if websocket:
                progress_dict = await _send_websocket_dump(
                    endpoint_name,
                    response,
                    service_response,
                    progress_dict,
                    websocket,
                )

            if service_response.status_code != 200:
                call_span.record_exception(
                    HTTPException(
                        status_code=service_response.status_code,
                        detail="Received non-200 from unpacked building block response",
                    ),
                    attributes={"status_code": service_response.status_code},
                )
                error_detail = f"Service {service} failed with error {service_response.msg_content}, endpoint: {endpoint_name}"
                call_span.set_status(StatusCode(2), error_detail)
                raise HTTPException(
                    status_code=service_response.status_code, detail=error_detail
                )

            if not service_response.should_continue:
                call_span.record_exception(
                    HTTPException(
                        status_code=400,
                        detail=f"Service: {service} returned should_continue",
                    ),
                    attributes={"status_code": 400},
                )
                error_detail = f"Service {service} completed, but orchestration cannot continue: {service_response.msg_content}"

                call_span.set_status(StatusCode(2), error_detail)
                raise HTTPException(
                    status_code=400,
                    detail=error_detail,
                )

            # Validation and save_bundle do not contain any updates to the data
            if service not in ["validation", "save_bundle"]:
                call_span.add_event(
                    "updating input data with building block modifications"
                )
                current_message = service_response.msg_content
            name = step.get("name", service)
            responses[name] = response
        call_span.set_status(StatusCode(1))
        return (response, responses)


def _param_dict_to_str(a_dict: dict):
    return [f"{k}: {v}" for k, v in (a_dict or {}).items()]
