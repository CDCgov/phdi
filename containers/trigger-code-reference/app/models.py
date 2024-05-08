from typing import List

from pydantic import BaseModel
from pydantic import Field
from pydantic import root_validator


class InsertConditionInput(BaseModel):
    """
    The schema for requests to the /insert-condition-extensions endpoint.
    """

    bundle: dict = Field(
        description="The FHIR bundle to modify. Each resource in the bundle related "
        "to one or more of the conditions in the other supplied parameter will have "
        "an extension added to the resource noting the SNOMED code relating to the "
        "associated condition(s)."
    )
    conditions: List[str] = Field(
        description="The list of SNOMED codes to insert as extensions into any "
        "associated resources in the supplied FHIR bundle."
    )

    @root_validator
    def require_non_empty_condition_list(cls, values):
        """
        Ensures that the supplied conditions list parameter is both a list
        and has at least one element by which to extend the supplied FHIR
        bundle.

        :param cls: The InsertConditionInput class.
        :param values: The condition list supplied by the caller.
        :raises ValueError: Errors when supplied condition list contains no
          elements, since this can't be used to extend a bundle.
        :return: The endpoint's values, if the condition list is valid.
        """
        if len(values.get("conditions")) == 0:
            raise ValueError(
                "Supplied list of SNOMED conditions must contain "
                "one or more elements; given list was empty."
            )
        return values
