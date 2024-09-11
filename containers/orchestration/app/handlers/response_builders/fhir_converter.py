from opentelemetry import trace
from opentelemetry.trace.status import StatusCode
from requests import Response

from app.handlers.ServiceHandlerResponse import ServiceHandlerResponse
from app.handlers.tracer import tracer


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
    with tracer.start_as_current_span(
        "unpack_fhir_converter_response",
        kind=trace.SpanKind(0),
        attributes={"status_code": response.status_code},
    ) as handler_span:
        match response.status_code:
            case 200:
                handler_span.add_event(
                    "conversion successful, dumping to JSON response struct"
                )
                converter_response = response.json().get("response")
                fhir_msg = converter_response.get("FhirResource")
                return ServiceHandlerResponse(response.status_code, fhir_msg, True)
            case _:
                handler_span.add_event("conversion failed")
                handler_span.set_status(
                    StatusCode(2), "Error Message: " + response.text
                )
                return ServiceHandlerResponse(
                    response.status_code,
                    f"FHIR Converter request failed: {response.text}",
                    False,
                )
