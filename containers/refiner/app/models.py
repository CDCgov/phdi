from typing import Optional
from typing import List

from pydantic import BaseModel
from pydantic import Field


class RefinerInput(BaseModel):
    """
    The schema for requests to the /refine endpoint.
    """

    include_headers: Optional[bool] = Field(
        description="Include headers in the output."
    )
    fields_to_include: Optional[List[str]] = Field(
        description="Fields to include in the refinement."
    )
    message: str = Field(description="The XML to refine.")


class RefinerResponse(BaseModel):
    """
    The schema for responses from the /refine endpoint.
    """

    status: str = Field(
        description="A message describing the result of a request to "
        "the /refine endpoint."
    )
    refined_message: str = Field(description="The refined XML.")
