from pydantic import BaseModel, Field


# Request and response models
class StandardizeInput(BaseModel):
    """
    A request model for the standardize endpoint.
    """

    unstandardized: str


class StandardizeResponse(BaseModel):
    """
    A response model for the standardize endpoint.
    """

    standardized: str


class HealthCheckResponse(BaseModel):
    """
    The schema for response from the Standardization health check endpoint.
    """

    status: str = Field(description="Returns status of this service")
