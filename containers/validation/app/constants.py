from typing import Literal
from typing import Optional

from pydantic import BaseModel
from pydantic import Field


# Request and and response models
class ValidateInput(BaseModel):
    """
    The schema for requests to the validate endpoint.
    """

    message_type: Literal["ecr", "elr", "vxu", "fhir"] = Field(
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
    rr_data: Optional[str] = Field(
        description="If validating an eICR message, the accompanying Reportability "
        "Response data.",
        default=None,
    )


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
