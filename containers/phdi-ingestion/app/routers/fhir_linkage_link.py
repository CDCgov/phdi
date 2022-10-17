from fastapi import APIRouter, Response, status
from pydantic import BaseModel, validator
from typing import Optional, Literal
import os

from phdi.fhir.linkage.link import add_patient_identifier_in_bundle

from app.utils import check_for_environment_variables, check_for_fhir_bundle


router = APIRouter(
    prefix="/fhir/linkage/link",
    tags=["fhir/linkage"],
)


class AddPatientIdentifierInBundleInput(BaseModel):
    bundle: dict
    salt_str: Optional[str] = ""
    overwrite: Optional[bool] = True

    _check_for_fhir = validator("bundle", allow_reuse=True)(check_for_fhir_bundle)


@router.post("/add_patient_identifier_in_bundle", status_code=200)
async def add_patient_identifier_in_bundle_endpoint(
    input: AddPatientIdentifierInBundleInput, response: Response
) -> dict:
    """
    Add a salted hash identifier to every patient resource in a FHIR bundle using. If
    a salt is not provided in the request the value of the 'SALT_STR' environment
    variable will be used. In the case where a salt is not provided and 'SALT_STR' is
    not defined and HTTP 500 status code is returned.

    :param input: A JSON formated request body with schema specified by the
        AddPatientIdentifierInBundleInput model.
    :return: A FHIR bundle where every patient resource contains a hashed identifier.
    """

    input = dict(input)

    if input.get("salt_str") in [None, ""]:
        check_result = check_for_environment_variables(["SALT_STR"])
        if check_result["status_code"] == 500:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return check_result
        else:
            input["salt_str"] = os.environ.get("SALT_STR")

    return add_patient_identifier_in_bundle(**input)
