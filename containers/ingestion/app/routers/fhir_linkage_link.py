from typing import Optional

from fastapi import APIRouter
from fastapi import Response
from fastapi import status
from pydantic import BaseModel
from pydantic import Field
from pydantic import validator

from app.fhir.linkage.link import add_patient_identifier_in_bundle
from app.utils import check_for_fhir_bundle
from app.utils import search_for_required_values
from app.utils import StandardResponse

router = APIRouter(
    prefix="/fhir/linkage/link",
    tags=["fhir/linkage"],
)


class AddPatientIdentifierInBundleInput(BaseModel):
    bundle: dict = Field(description="A FHIR bundle")
    salt_str: Optional[str] = Field(
        description="The salt to use with the hash. This is intended to prevent reverse"
        " engineering of the PII used to create the hash.",
        default="",
    )
    overwrite: Optional[bool] = Field(
        description="If true, `data` is modified in-place; if false, a copy of `data` "
        "modified and returned.",
        default=True,
    )

    _check_for_fhir_bundle = validator("bundle", allow_reuse=True)(
        check_for_fhir_bundle
    )


@router.post("/add_patient_identifier_in_bundle", status_code=200)
async def add_patient_identifier_in_bundle_endpoint(
    input: AddPatientIdentifierInBundleInput, response: Response
) -> StandardResponse:
    """
    This endpoint adds a salted hash identifier to every patient resource
    in a FHIR bundle . If a salt isn't provided in the request, the value of
    the 'SALT_STR' environment variable will be used. In the case where a salt
    isn't  provided and 'SALT_STR' isn't defined, an HTTP 500 status code will
    be returned.

    ### Inputs and Outputs
    - :param input: A JSON formatted request body with schema specified by the
        AddPatientIdentifierInBundleInput model.
    - :return: A FHIR bundle where every patient resource contains a hashed identifier.
    """

    input = dict(input)
    required_values = ["salt_str"]
    search_result = search_for_required_values(input, required_values)
    if search_result != "All values were found.":
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status_code": "400", "message": search_result}

    return {"status_code": "200", "bundle": add_patient_identifier_in_bundle(**input)}
