from pydantic import BaseModel
from pydantic import Field


class RefineECRRequest(BaseModel):
    """
    Model for the /ecr endpoint.
    """

    refiner_input: str = Field(
        description="The request object containing the XML input."
    )
    sections_to_include: str = Field(
        None, description="The fields to include in the refined message."
    )
    conditions_to_include: str = Field(
        None,
        description="The SNOMED condition codes to use to search for relevant clinical services in the ECR.",
    )


class RefineECRResponse(BaseModel):
    """
    Return for the /ecr endpoint.
    """

    refined_message: str = Field(description="Refined XML as a string.")
