from pydantic import BaseModel
from pydantic import Field


class RefinerInput(BaseModel):
    """
    The schema for requests to the /refine endpoint.
    """

    message: str = Field(description="The XML to refine.")


class RefinerResponse(BaseModel):
    """
    The schema for responses from the /refine endpoint.
    """

    refined_message: str = Field(description="The refined XML.")
