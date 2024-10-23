from opentelemetry import trace

from app.handlers.tracer import tracer
from app.models import OrchestrationRequest

MESSAGE_TO_TEMPLATE_MAP = {
    "fhir": "",
    "ecr": "EICR",
    "elr": "ORU_R01",
    "vxu": "VXU_V04",
}


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
    with tracer.start_as_current_span(
        "build_fhir_converter_request",
        kind=trace.SpanKind(0),
        attributes={
            "message_type": orchestration_request.get("message_type"),
            "data_type": orchestration_request.get("data_type"),
            "workflow_params": str(workflow_params),
        },
    ) as handler_span:
        # Template will depend on input data formatting and typing
        input_type = orchestration_request.get("message_type")
        root_template = MESSAGE_TO_TEMPLATE_MAP[input_type]
        handler_span.add_event(
            "identified root template type for conversion",
            attributes={"root_template": root_template},
        )
        return {
            "input_data": input_msg,
            "input_type": input_type,
            "root_template": root_template,
            "rr_data": orchestration_request.get("rr_data"),
        }
