from app.handlers import tracer
from app.handlers.ServiceHandlerResponse import ServiceHandlerResponse
from opentelemetry import trace
from opentelemetry.trace.status import StatusCode
from requests import Response


def unpack_stamp_condition_extensions_response(
    response: Response,
) -> ServiceHandlerResponse:
    """
    Helper function for processing a response from trigger code reference service's stamp conditions extension endpoint.

    If the status code of the response the server sent back is OK, return
    the message from the response body. Otherwise, report what
    went wrong based on status_code.

    :param response: The response returned by a POST request to the ingestion service.
    :return: A tuple containing the status code of the response as well as
      parsed message created by the service.
    """
    with tracer.start_as_current_span(
        "unpack_stamp_condition_extensions_response",
        kind=trace.SpanKind(0),
        attributes={"status_code": response.status_code},
    ) as handler_span:
        status_code = response.status_code

        match status_code:
            case 200:
                handler_span.add_event("stamp condition extensions succeeded")
                return ServiceHandlerResponse(
                    status_code,
                    response.json().get("extended_bundle"),
                    True,
                )
            case 400:
                handler_span.add_event(
                    "trigger code reference service responded with bad request"
                )
                handler_span.set_status(
                    StatusCode(2), "Error Message: " + response.json().get("message")
                )
                return ServiceHandlerResponse(
                    status_code, response.json().get("message"), False
                )
            case 422:
                handler_span.add_event(
                    "trigger code reference service responded with unprocessable entity / bad input params"
                )
                handler_span.set_status(
                    StatusCode(2), "Error Message: " + response.json().__str__()
                )
                return ServiceHandlerResponse(status_code, response.json(), False)
            case _:
                handler_span.add_event("stamp condition extensions failed")
                handler_span.set_status(
                    StatusCode(2), "Error Message: " + response.text
                )
                return ServiceHandlerResponse(
                    status_code,
                    f"Stamping condition extensions failed: {response.text}",
                    False,
                )
