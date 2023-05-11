import json
import pathlib

from fastapi import APIRouter
from pydantic import BaseModel, validator, Field
from typing import Literal, Optional

from app.utils import check_for_fhir, StandardResponse

from phdi.fhir.harmonization.standardization import (
    standardize_names,
    standardize_phones,
    standardize_dob,
)

router = APIRouter(
    prefix="/fhir/harmonization/standardization",
    tags=["fhir/harmonization"],
)

# Sample request/response for name endpoint
sample_name_request_data = json.load(
    open(
        (
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "sample_standardize_name_request_data.json"
        )
    )
)

raw_sample_name_response = json.load(
    open(
        (
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "sample_standardize_name_response.json"
        )
    )
)

sample_name_response = {200: raw_sample_name_response}


class StandardizeNamesInput(BaseModel):
    data: dict = Field(
        description="A FHIR resource or bundle in JSON format.",
        example=sample_name_request_data,
    )
    trim: Optional[bool] = Field(
        description="When true, leading and trailing spaces are removed", default=True
    )
    overwrite: Optional[bool] = Field(
        description="If true, `data` is modified in-place; if false, a copy of `data` "
        "is modified and returned.",
        default=True,
    )
    case: Optional[Literal["upper", "lower", "title"]] = Field(
        descripton="The type of casing that should be used.", default="upper"
    )
    remove_numbers: Optional[bool] = Field(
        description="If true, delete numeric characters; if false leave numbers in "
        "place.",
        default=True,
    )

    _check_for_fhir = validator("data", allow_reuse=True)(check_for_fhir)


@router.post("/standardize_names", responses=sample_name_response)
async def standardize_names_endpoint(input: StandardizeNamesInput) -> StandardResponse:
    """
    Standardize the names in the provided FHIR bundle or resource.

    :param input: A dictionary with the schema specified by the StandardizeNamesInput
        model.

    :return: A FHIR bundle or resource with standardized names.
    """
    input = dict(input)
    return {"status_code": "200", "bundle": standardize_names(**input)}


# Sample request/response for phone endpoint
sample_phone_request_data = json.load(
    open(
        (
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "sample_standardize_phone_request_data.json"
        )
    )
)

raw_sample_phone_response = json.load(
    open(
        (
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "sample_standardize_phone_response.json"
        )
    )
)

sample_phone_response = {200: raw_sample_phone_response}


class StandardizePhonesInput(BaseModel):
    data: dict = Field(
        description="A FHIR resource or bundle in JSON format.",
        example=sample_phone_request_data,
    )
    overwrite: Optional[bool] = Field(
        description="If true, `data` is modified in-place; if false, a copy of `data` "
        "is modified and returned.",
        default=True,
    )

    _check_for_fhir = validator("data", allow_reuse=True)(check_for_fhir)


@router.post("/standardize_phones", responses=sample_phone_response)
async def standardize_phones_endpoint(
    input: StandardizePhonesInput,
) -> StandardResponse:
    """
    Standardize the phone numbers in the provided FHIR bundle or resource.

    Requires an address so that country code can be generated.

    :param input: A dictionary with the schema specified by the StandardizePhonesInput
        model.

    :return: A FHIR bundle with standardized phone numbers.
    """
    input = dict(input)
    return {"status_code": "200", "bundle": standardize_phones(**input)}


# Sample request/response for date of birth endpoint
# this read_from_assets thing isn't working yet - need to revisit
# sample_date_of_birth_request_data = read_json_from_assets(
#     "sample_standardize_date_of_birth_request_data.json"
# )
# TODO tomorrow:
# X. Finish the sample request (test with Insomnia to make sure it's valid)
# X. Create a sample response from the request
# X. Make sure all of those are working with the docs
# 4. Try to get this utility function working to read from assets
# 5. Push up the PR
sample_date_of_birth_request_data = json.load(
    open(
        (
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "sample_standardize_date_of_birth_request_data.json"
        )
    )
)

raw_sample_date_of_birth_response = json.load(
    open(
        (
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "sample_standardize_date_of_birth_response.json"
        )
    )
)

sample_date_of_birth_response = {200: raw_sample_date_of_birth_response}


class StandardizeBirthDateInput(BaseModel):
    data: dict = Field(
        description="A FHIR resource or bundle in JSON format.",
        example=sample_date_of_birth_request_data,
    )
    overwrite: Optional[bool] = Field(
        description="If true, `data` is modified in-place; if false, a copy of `data` "
        "is modified and returned.",
        default=True,
    )
    format: Optional[str] = Field(
        descripton="The date format that the input DOB is supplied in.",
        default="Y%-m%-d%",
        example="%m/%d/%Y",
    )

    _check_for_fhir = validator("data", allow_reuse=True)(check_for_fhir)


@router.post("/standardize_dob", responses=sample_date_of_birth_response)
async def standardize_dob_endpoint(
    input: StandardizeBirthDateInput,
) -> StandardResponse:
    """
    Standardize the patient date of birth in the provided FHIR bundle or resource.

    Dates are changed to the FHIR standard of YYYY-MM-DD.

    Returns a FHIR bundle with standardized birth dates.
    """
    input = dict(input)
    result = {}
    try:
        standardized_bundles = standardize_dob(**input)
        result["status_code"] = "200"
        result["bundle"] = standardized_bundles
    except Exception as error:
        result["status_code"] = "400"
        result["bundle"] = input["data"]
        result["message"] = error.__str__()
    return result
