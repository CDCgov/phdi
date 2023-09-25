from typing import Annotated
from fastapi import Body
from pathlib import Path
from phdi.containers.base_service import BaseService
from phdi.validation.validation import validate_ecr
from .utils import (
    load_ecr_config,
    validate_error_types,
    read_json_from_assets,
    check_for_and_extract_rr_data,
)
from .constants import ValidateInput, ValidateResponse

# TODO: Remove hard coded location for config path
# and/or provide a mechanism to pass in configuration
#  via endpoint
ecr_config = load_ecr_config()

# Instantiate FastAPI via PHDI's BaseService class
app = BaseService(
    service_name="PHDI Validation Service",
    description_path=Path(__file__).parent.parent / "description.md",
).start()


# Message type-specific validation
def validate_ecr_msg(message: str, include_error_types: list) -> ValidateResponse:
    """
    Validate an XML-formatted CDA eCR message.
    :param message: A string representation of an eCR in XML format to be validated.
    :param include_error_types: A list of the error types to include in validation.
    :return: A dictionary with keys and values described by the ValidateResponse class.
    """

    response_dict = validate_ecr(
        ecr_message=message, config=ecr_config, include_error_types=include_error_types
    )
    return ValidateResponse(
        message_valid=response_dict.get("message_valid"),
        validation_results=response_dict.get("validation_results"),
    )


def validate_elr_msg(message: str, include_error_types: list) -> ValidateResponse:
    """
    Validate an HL7v2 ORU_R01 ELR message.
    :param message: A string representation of an HL7v2 ORU_R01 message to be validated.
    :return: A dictionary with keys and values described by the ValidateResponse class.
    """

    details = {
        "details": "No validation was actually performed. Validation for ELR is "
        "only stubbed currently."
    }
    return ValidateResponse(message_valid=True, validation_results=details)


def validate_vxu_msg(message: str, include_error_types: list) -> ValidateResponse:
    """
    Validate an HL7v2 VXU_04 VXU message.
    :param message: A string representation of a HL7v2 VXU_04 message to be validated.
    :return: A dictionary with keys and values described by the ValidateResponse class.
    """

    details = {
        "details": "No validation was actually performed. Validation for VXU is "
        "only stubbed currently."
    }
    return ValidateResponse(message_valid=True, validation_results=details)


def validate_fhir_bundle(message: str, include_error_types: list) -> ValidateResponse:
    """
    Validate a FHIR bundle.
    :param message: A string representation of a FHIR bundle to be validated.
    :return: A dictionary with keys and values described by the ValidateResponse class.
    """

    details = {
        "details": "No validation was actually performed. Validation for FHIR is "
        "only stubbed currently."
    }
    return ValidateResponse(message_valid=True, validation_results=details)


message_validators = {
    "ecr": validate_ecr_msg,
    "elr": validate_elr_msg,
    "vxu": validate_vxu_msg,
    "fhir": validate_fhir_bundle,
}

# Sample requests and responses for docs
sample_validate_requests = read_json_from_assets("sample_validate_requests.json")
sample_validate_responses = read_json_from_assets("sample_validate_responses.json")


# Endpoints
@app.post("/validate", status_code=200, responses={200: sample_validate_responses})
async def validate_endpoint(
    input: Annotated[ValidateInput, Body(examples=sample_validate_requests)]
) -> ValidateResponse:
    """
    Check if the value presented in the 'message' key is a valid example
    of the type of message specified in the 'message_type'.
    """

    input = dict(input)
    message_validator = message_validators[input["message_type"]]
    include_error_types = validate_error_types(input["include_error_types"])
    input_to_validate = check_for_and_extract_rr_data(input)
    msg = input_to_validate["message"]

    return message_validator(message=msg, include_error_types=include_error_types)
