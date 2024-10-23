from opentelemetry import trace

from app.handlers.tracer import tracer
from app.models import OrchestrationRequest


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
    with tracer.start_as_current_span(
        "build_message_parser_parse_message_request",
        kind=trace.SpanKind(0),
        attributes={
            "message_type": orchestration_request.get("message_type"),
            "data_type": orchestration_request.get("data_type"),
            "workflow_params": str(workflow_params),
        },
    ) as handler_span:
        # Template format will depend on the data's structure
        if (
            isinstance(input_msg, dict)
            and input_msg.get("resourceType", "") == "Bundle"
        ):
            msg_fmt = "fhir"
        else:
            msg_fmt = orchestration_request.get("message_type")
        handler_span.add_event("using message format " + msg_fmt)
        return {
            "message": input_msg,
            "message_format": msg_fmt,
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
    with tracer.start_as_current_span(
        "build_message_parser_phdc_request",
        kind=trace.SpanKind(0),
        attributes={
            "message_type": orchestration_request.get("message_type"),
            "data_type": orchestration_request.get("data_type"),
            "workflow_params": str(workflow_params),
        },
    ):
        return {
            "message": input_msg,
            "phdc_report_type": workflow_params.get("phdc_report_type"),
        }
