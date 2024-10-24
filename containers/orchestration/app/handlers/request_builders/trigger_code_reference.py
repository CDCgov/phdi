from opentelemetry import trace

from app.handlers.tracer import tracer
from app.models import OrchestrationRequest


def build_stamp_condition_extensions_request(
    input_msg: str,
    orchestration_request: OrchestrationRequest,
    workflow_params: dict | None = None,
) -> dict:
    """
    Helper function for constructing the output payload for an API call to
    the DIBBs trigger code reference service.

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
        "build_stamp_condition_extensions_request",
        kind=trace.SpanKind(0),
        attributes={
            "message_type": orchestration_request.get("message_type"),
            "data_type": orchestration_request.get("data_type"),
            "workflow_params": str(workflow_params),
        },
    ):
        # Initialize workflow_params as an empty dictionary if it's None
        workflow_params = workflow_params or {}

        return {
            "bundle": input_msg,
            "conditions": workflow_params.get("conditions"),
        }
