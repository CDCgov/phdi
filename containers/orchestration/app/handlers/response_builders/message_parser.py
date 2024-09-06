from opentelemetry import trace
from opentelemetry.trace.status import StatusCode
from requests import Response

from app.handlers.ServiceHandlerResponse import ServiceHandlerResponse
from app.handlers.tracer import tracer


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
    with tracer.start_as_current_span(
        "unpack_parsed_message_response",
        kind=trace.SpanKind(0),
        attributes={"status_code": response.status_code},
    ) as handler_span:
        status_code = response.status_code

        match status_code:
            case 200:
                handler_span.add_event("Successfully parsed extracted values")
                return ServiceHandlerResponse(
                    status_code, response.json().get("parsed_values"), True
                )
            case 400:
                handler_span.add_event("Message parser responded with bad request")
                handler_span.set_status(
                    StatusCode(2), "Error Message: " + response.json().get("message")
                )
                return ServiceHandlerResponse(
                    status_code, response.json().get("message"), False
                )
            case 422:
                handler_span.add_event(
                    "Message parser responded with unprocessable entity / bad input parameters"
                )
                handler_span.set_status(
                    StatusCode(2), "Error Message: " + response.json().__str__()
                )
                return ServiceHandlerResponse(status_code, response.json(), False)
            case _:
                handler_span.add_event("Message parser failed")
                handler_span.set_status(
                    StatusCode(2), "Error Message: " + response.text
                )
                return ServiceHandlerResponse(
                    status_code,
                    f"Message Parser request failed: {response.text}",
                    False,
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
    with tracer.start_as_current_span(
        "unpack_fhir_to_phdc_response",
        kind=trace.SpanKind(0),
        attributes={"status_code": response.status_code},
    ) as handler_span:
        status_code = response.status_code

        match status_code:
            case 200:
                handler_span.add_event("Successfully constructed PHDC from bundle")
                return ServiceHandlerResponse(status_code, response.content, True)
            case 422:
                handler_span.add_event(
                    "Message parser responded with unprocessable entity / bad input parameters"
                )
                handler_span.set_status(
                    StatusCode(2), "Error Message: " + response.json().__str__()
                )
                return ServiceHandlerResponse(status_code, response.json(), False)
            case _:
                handler_span.add_event("PHDC construction failed")
                handler_span.set_status(
                    StatusCode(2), "Error Message: " + response.text
                )
                return ServiceHandlerResponse(
                    status_code,
                    f"Message Parser request failed: {response.text}",
                    False,
                )
