from fastapi import HTTPException

from phdi.fhir.conversion.convert import _get_fhir_conversion_settings
from phdi.fhir.conversion.convert import standardize_hl7_datetimes


def build_fhir_converter_request(input_msg: str, rr_data: str | None = None) -> dict:
    """
    Helper function for constructing the input payload for an API call to
    the DIBBs FHIR converter. When the user uploads data, we use the
    properties of the uploaded message to determine the appropriate
    conversion settings (such as the root template or HL7v2 basis segment).
    If these values cannot be determined directly from the message, the
    payload is set with default permissive EICR templates to allow the
    broadest range of conversion.

    :param input_msg: The data the user sent for workflow processing, as
      a string.
    :param rr_data: Optionally, the reportability response data associated
      with the message, if the message is an eCR.
    :return: A dictionary ready to JSON-serialize as a payload to the
      FHIR converter.
    """
    # Template will depend on input data formatting and typing, so try
    # to figure that out. If we can't, use our default EICR settings
    # to preserve backwards compatibility
    try:
        conversion_settings = _get_fhir_conversion_settings(input_msg)
        if conversion_settings["input_type"] == "hl7v2":
            input_msg = standardize_hl7_datetimes(input_msg)
    except KeyError:
        conversion_settings = {"input_type": "ecr", "root_template": "EICR"}
    return {
        "input_data": input_msg,
        "input_type": conversion_settings["input_type"],
        "root_template": conversion_settings["root_template"],
        "rr_data": rr_data,
    }


def unpack_fhir_converter_response(response: dict) -> dict:
    """
    Helper functoin for processing a response from the DIBBs FHIR converter.
    If the status code of the response the server sent back is OK, return
    the parsed FHIR bundle from the response body. Otherwise, report what
    went wrong.

    :param response: The response returned by a POST request to the FHIR
      converter.
    :return: The FHIR bundle that the service generated.
    """
    converter_response = response.json().get("response")
    print(converter_response)
    if converter_response.status_code != 200:
        raise HTTPException(
            status_code=converter_response.status_code,
            detail={"error": "Bad Request", "details": "FHIR conversion failed"},
        )
    fhir_msg = converter_response.get("FhirResource")
    return fhir_msg
