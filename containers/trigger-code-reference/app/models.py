from pydantic import BaseModel
from pydantic import Field


class InsertConditionInput(BaseModel):
    """
    The schema for requests to the /insert-condition-extensions endpoint.
    """

    bundle: dict = Field(
        description="The FHIR bundle to modify. Each resource in the bundle related "
        "to one or more of the conditions found in the bundle will have "
        "an extension added to the resource noting the SNOMED code relating to the "
        "associated condition(s)."
    )
