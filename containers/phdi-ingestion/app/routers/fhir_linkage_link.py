from fastapi import APIRouter, Response, status
from pydantic import BaseModel, validator
from typing import Optional

from phdi.fhir.linkage.link import add_patient_identifier_in_bundle

from app.utils import (
    check_for_fhir_bundle,
    search_for_required_values,
    StandardResponse,
)


router = APIRouter(
    prefix="/fhir/linkage/link",
    tags=["fhir/linkage"],
)


class AddPatientIdentifierInBundleInput(BaseModel):
    bundle: dict
    salt_str: Optional[str] = ""
    overwrite: Optional[bool] = True

    _check_for_fhir_bundle = validator("bundle", allow_reuse=True)(
        check_for_fhir_bundle
    )


@router.post("/add_patient_identifier_in_bundle", status_code=200)
async def add_patient_identifier_in_bundle_endpoint(
    input: AddPatientIdentifierInBundleInput, response: Response
) -> StandardResponse:
    """
    Add a salted hash identifier to every patient resource in a FHIR bundle using. If
    a salt is not provided in the request the value of the 'SALT_STR' environment
    variable will be used. In the case where a salt is not provided and 'SALT_STR' is
    not defined an HTTP 500 status code is returned.

    :param input: A JSON formated request body with schema specified by the
        AddPatientIdentifierInBundleInput model.
    :return: A FHIR bundle where every patient resource contains a hashed identifier.
    """

    input = dict(input)
    required_values = ["salt_str"]
    search_result = search_for_required_values(input, required_values)
    if search_result != "All values were found.":
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status_code": "400", "message": search_result}

    return {"status_code": "200", "bundle": add_patient_identifier_in_bundle(**input)}
