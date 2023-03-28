from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Literal
from pathlib import Path
from phdi.validation.validation import validate_ecr
from .utils import load_ecr_config, validate_error_types

# TODO: Remove hard coded location for config path
# and/or provide a mechanism to pass in configuration
#  via endpoint
ecr_config = load_ecr_config()


# Instantiate FastAPI and set metadata.
description = Path("description.md").read_text(encoding="utf-8")
app = FastAPI(
    title="PHDI Validation Service",
    version="0.0.1",
    contact={
        "name": "CDC Public Health Data Infrastructure",
        "url": "https://cdcgov.github.io/phdi-site/",
        "email": "dmibuildingblocks@cdc.gov",
    },
    license_info={
        "name": "Creative Commons Zero v1.0 Universal",
        "url": "https://creativecommons.org/publicdomain/zero/1.0/",
    },
    description=description,
)


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
            "details": "No validation was actually preformed. This endpoint only has "
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
            "details": "No validation was actually preformed. This endpoint only has "
            "stubbed functionality"
        },
    }


message_validators = {
    "ecr": validate_ecr_msg,
    "elr": validate_elr_msg,
    "vxu": validate_vxu_msg,
}


# Endpoints
@app.get("/")
async def health_check():
    """
    Check service status. If an HTTP 200 status code is returned along with
    '{"status": "OK"}' then the tabulation service is available and running properly.
    """
    return {"status": "OK"}


@app.post("/validate", status_code=200)
async def validate_endpoint(input: ValidateInput) -> ValidateResponse:
    """
    Check if the value presented in the 'message' key is a valid example
    of the type of message specified in the 'message_type'.
    :param input: A JSON formatted request body with schema specified by the
        ValidateInput model.
    :return: A JSON formatted response body with schema specified
        by the ValidateResponse model.
    """

    input = dict(input)
    message_validator = message_validators[input["message_type"]]
    include_error_types = validate_error_types(input["include_error_types"])
    msg = input["message"]

    return message_validator(message=msg, include_error_types=include_error_types)
