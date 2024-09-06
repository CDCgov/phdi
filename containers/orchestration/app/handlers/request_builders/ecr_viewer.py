from app.handlers import tracer
from app.models import OrchestrationRequest
from opentelemetry import trace


def build_save_fhir_data_body(
    input_msg: str,
    orchestration_request: OrchestrationRequest,
    workflow_params: dict | None = None,
) -> dict:
    """
    Helper function for constructing the input payload for an API call to
    the DIBBs ecr viewer.

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
        "build_save_fhir_data_body_request",
        kind=trace.SpanKind(0),
        attributes={
            "message_type": orchestration_request.get("message_type"),
            "data_type": orchestration_request.get("data_type"),
            "workflow_params": workflow_params,
        },
    ):
        return {
            "fhirBundle": input_msg,
            "saveSource": workflow_params.get("saveSource"),
        }
