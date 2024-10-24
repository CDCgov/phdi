import os

from opentelemetry import trace

from app.handlers.tracer import tracer
from app.models import OrchestrationRequest


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
    with tracer.start_as_current_span(
        "build_validation_request",
        kind=trace.SpanKind(0),
        attributes={
            "message_type": orchestration_request.get("message_type"),
            "data_type": orchestration_request.get("data_type"),
            "workflow_params": str(workflow_params),
        },
    ):
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
    with tracer.start_as_current_span(
        "build_ingestion_name_standardization_request",
        kind=trace.SpanKind(0),
        attributes={
            "message_type": orchestration_request.get("message_type"),
            "data_type": orchestration_request.get("data_type"),
            "workflow_params": str(workflow_params),
        },
    ) as handler_span:
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

        handler_span.add_event(
            "updating standardization options",
            attributes={
                "trim": workflow_params.get("trim"),
                "overwrite": workflow_params.get("overwrite"),
                "case": workflow_params.get("case"),
                "remove_numbers": workflow_params.get("remove_numbers"),
            },
        )

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
    with tracer.start_as_current_span(
        "build_ingestion_phone_standardization_request",
        kind=trace.SpanKind(0),
        attributes={
            "message_type": orchestration_request.get("message_type"),
            "data_type": orchestration_request.get("data_type"),
            "workflow_params": str(workflow_params),
        },
    ):
        # Since only one param, just add it explicitly
        if not workflow_params:
            workflow_params = {"overwrite": "true"}

        return {
            "data": input_msg,
            "overwrite": workflow_params.get("overwrite", "true"),
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
    with tracer.start_as_current_span(
        "build_ingestion_dob_standardization_request",
        kind=trace.SpanKind(0),
        attributes={
            "message_type": orchestration_request.get("message_type"),
            "data_type": orchestration_request.get("data_type"),
            "workflow_params": str(workflow_params),
        },
    ) as handler_span:
        # Default parameter values
        default_params = {"overwrite": "true", "format": "Y%-m%-d%"}

        # Initialize workflow_params as an empty dictionary if it's None
        workflow_params = workflow_params or {}

        for key, value in default_params.items():
            workflow_params.setdefault(key, value)

        handler_span.add_event(
            "updating standardization options",
            attributes={
                "overwrite": workflow_params.get("overwrite"),
                "format": workflow_params.get("format"),
            },
        )

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
    with tracer.start_as_current_span(
        "build_geocoding_request",
        kind=trace.SpanKind(0),
        attributes={
            "message_type": orchestration_request.get("message_type"),
            "data_type": orchestration_request.get("data_type"),
            "workflow_params": str(workflow_params),
        },
    ) as handler_span:
        # Default parameter values
        default_params = {
            "geocode_method": "smarty",
            "smarty_auth_id": os.environ.get("SMARTY_AUTH_ID"),
            "smarty_auth_token": os.environ.get("SMARTY_AUTH_TOKEN"),
            "license_type": "us-rooftop-geocoding-enterprise-cloud",
            "overwrite": "true",
        }

        # Initialize workflow_params as an empty dictionary if it's None
        workflow_params = workflow_params or {}

        for key, value in default_params.items():
            workflow_params.setdefault(key, value)

        handler_span.add_event(
            "updating geocoding function parameters",
            attributes={
                "geocode_method": workflow_params.get("geocode_method"),
                "smarty_auth_id_is_not_null": workflow_params.get("smarty_auth_id")
                is not None,
                "smarty_auth_token_is_not_null": workflow_params.get(
                    "smarty_auth_token"
                )
                is not None,
                "license_type": workflow_params.get("license_type"),
                "overwrite": workflow_params.get("overwrite"),
            },
        )

        return {
            "bundle": input_msg,
            "geocode_method": workflow_params.get("geocode_method"),
            "smarty_auth_id": workflow_params.get("smarty_auth_id"),
            "smarty_auth_token": workflow_params.get("smarty_auth_token"),
            "license_type": workflow_params.get("license_type"),
            "overwrite": workflow_params.get("overwrite"),
        }
