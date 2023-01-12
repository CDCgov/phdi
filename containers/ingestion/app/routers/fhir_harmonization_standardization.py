from fastapi import APIRouter
from pydantic import BaseModel, validator, Field
from typing import Literal, Optional

from app.utils import check_for_fhir, StandardResponse

from phdi.fhir.harmonization.standardization import standardize_names
from phdi.fhir.harmonization.standardization import standardize_phones


router = APIRouter(
    prefix="/fhir/harmonization/standardization",
    tags=["fhir/harmonization"],
)


class StandardizeNamesInput(BaseModel):
    data: dict = Field(description="A FHIR resource or bundle in JSON format.")
    trim: Optional[bool] = Field(
        description="When true, leading and trailing spaces are removed", default=True
    )
    overwrite: Optional[bool] = Field(
        description="If true, `data` is modified in-place; if false, a copy of `data` "
        "modified and returned.",
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


@router.post("/standardize_names")
async def standardize_names_endpoint(input: StandardizeNamesInput) -> StandardResponse:
    """
    Standardize the names in the provided FHIR bundle or resource.
    :param input: A dictionary with the schema specified by the StandardizeNamesInput
        model.
    :return: A FHIR bundle or resource with standardized names.
    """
    input = dict(input)
    return {"status_code": "200", "bundle": standardize_names(**input)}


class StandardizePhonesInput(BaseModel):
    data: dict = Field(description="A FHIR resource or bundle in JSON format.")
    overwrite: Optional[bool] = Field(
        description="If true, `data` is modified in-place; if false, a copy of `data` "
        "modified and returned.",
        default=True,
    )

    _check_for_fhir = validator("data", allow_reuse=True)(check_for_fhir)


@router.post("/standardize_phones")
async def standardize_phones_endpoint(
    input: StandardizePhonesInput,
) -> StandardResponse:
    """
    Standardize the phone numbers in the provided FHIR bundle or resource.
    :param input: A dictionary with the schema specified by the StandardizePhonesInput
        model.
    :return: A FHIR bundle with standardized phone numbers.
    """
    input = dict(input)
    return {"status_code": "200", "bundle": standardize_phones(**input)}
