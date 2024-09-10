from opentelemetry import trace
from opentelemetry.trace.status import StatusCode
from requests import Response

from app.handlers.ServiceHandlerResponse import ServiceHandlerResponse
from app.handlers.tracer import tracer


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
    with tracer.start_as_current_span(
        "unpack_validation_response",
        kind=trace.SpanKind(0),
        attributes={"status_code": response.status_code},
    ) as handler_span:
        match response.status_code:
            case 200:
                validator_response = response.json()
                handler_span.add_event(
                    "Validation service completed successfully",
                    attributes={
                        "validation_results": validator_response.get(
                            "validation_results"
                        ),
                        "message_is_valid": validator_response.get("message_valid"),
                    },
                )
                return ServiceHandlerResponse(
                    response.status_code,
                    validator_response.get("validation_results"),
                    validator_response.get("message_valid"),
                )
            case _:
                handler_span.add_event(
                    "Validation of message failed, or message contained errors"
                )
                handler_span.set_status(
                    StatusCode(2), "Error Message: " + response.text
                )
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
    with tracer.start_as_current_span(
        "unpack_ingestion_standardization_response",
        kind=trace.SpanKind(0),
        attributes={"status_code": response.status_code},
    ) as handler_span:
        status_code = response.status_code

        match status_code:
            case 200:
                handler_span.add_event("ingestion operation successful")
                return ServiceHandlerResponse(
                    status_code,
                    response.json().get("bundle"),
                    True,
                )
            case 400:
                handler_span.add_event("ingestion service responded with bad request")
                handler_span.set_status(
                    StatusCode(2), "Error Message: " + response.json().get("message")
                )
                return ServiceHandlerResponse(
                    status_code, response.json().get("message"), False
                )
            case 422:
                handler_span.add_event(
                    "ingestion service responded with unprocessable entity / bad input params"
                )
                handler_span.set_status(
                    StatusCode(2), "Error Message: " + response.json().__str__()
                )
                return ServiceHandlerResponse(status_code, response.json(), False)
            case _:
                handler_span.add_event("ingestion service failed")
                handler_span.set_status(
                    StatusCode(2), "Error Message: " + response.text
                )
                return ServiceHandlerResponse(
                    status_code,
                    f"Standardization request failed: {response.text}",
                    False,
                )
