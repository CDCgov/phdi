from pydantic import BaseModel, Field
from typing import Literal, Annotated
from fastapi import Body
from pathlib import Path
from phdi.containers.base_service import BaseService
from phdi.validation.validation import validate_ecr
from .utils import load_ecr_config, validate_error_types, read_json_from_assets

# TODO: Remove hard coded location for config path
# and/or provide a mechanism to pass in configuration
#  via endpoint
ecr_config = load_ecr_config()


# Instantiate FastAPI via PHDI's BaseService class
app = BaseService(
    service_name="PHDI Validation Service",
    description_path=Path(__file__).parent.parent / "description.md",
).start()


# Request and and response models
class ValidateInput(BaseModel):
    """
    The schema for requests to the validate endpoint.
    """

    message_type: Literal["ecr", "elr", "vxu"] = Field(
        description="The type of message to be validated."
    )
    include_error_types: str = Field(
        description=(
            "A comma separated list of the types of errors that should be"
            + " included in the return response."
            + " Valid types are fatal, errors, warnings, information"
        )
    )
    message: str = Field(description="The message to be validated.")


class ValidateResponse(BaseModel):
    """
    The schema for response from the validate endpoint.
    """

    message_valid: bool = Field(
        description="A true value indicates a valid message while false means that the "
        "message was found to be invalid."
    )
    validation_results: dict = Field(
        description="A JSON object containing details on the validation result."
    )


# Message type-specific validation
def validate_ecr_msg(message: str, include_error_types: list) -> ValidateResponse:
    """
    Validate an XML-formatted CDA eCR message.
    :param message: A string representation of an eCR in XML format to be validated.
    :return: A dictionary with keys and values described by the ValidateResponse class.
    """

    return validate_ecr(
        ecr_message=message, config=ecr_config, include_error_types=include_error_types
    )


def validate_elr_msg(message: str, include_error_types: list) -> ValidateResponse:
    """
    Validate an HL7v2 ORU_R01 ELR message.
    :param message: A string representation of an HL7v2 ORU_R01 message to be validated.
    :return: A dictionary with keys and values described by the ValidateResponse class.
    """

    return {
        "message_valid": True,
        "validation_results": {
            "details": "No validation was actually performed. This endpoint only has "
            "stubbed functionality"
        },
    }


def validate_vxu_msg(message: str, include_error_types: list) -> ValidateResponse:
    """
    Validate an HL7v2 VXU_04 VXU message.
    :param message: A string representation of a HL7v2 VXU_04 message to be validated.
    :return: A dictionary with keys and values described by the ValidateResponse class.
    """

    return {
        "message_valid": True,
        "validation_results": {
            "details": "No validation was actually performed. This endpoint only has "
            "stubbed functionality"
        },
    }


message_validators = {
    "ecr": validate_ecr_msg,
    "elr": validate_elr_msg,
    "vxu": validate_vxu_msg,
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
    msg = input["message"]

    return message_validator(message=msg, include_error_types=include_error_types)
