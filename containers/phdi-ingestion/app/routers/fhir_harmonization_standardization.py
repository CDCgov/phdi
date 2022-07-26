from fastapi import APIRouter
from pydantic import BaseModel, validator
from typing import Literal, Optional

from app.utils import check_for_fhir

from phdi.fhir.harmonization.standardization import standardize_names
from phdi.fhir.harmonization.standardization import standardize_phones


router = APIRouter(
    prefix="/fhir/harmonization/standardization",
    tags=["fhir/harmonization"],
)


class StandardizeNamesInput(BaseModel):
    data: dict
    trim: Optional[bool] = True
    overwrite: Optional[bool] = True
    case: Optional[Literal["upper", "lower", "title"]] = "upper"
    remove_numbers: Optional[bool] = True

    _check_for_fhir = validator("data", allow_reuse=True)(check_for_fhir)


@router.post("/standardize_names")
async def standardize_names_endpoint(input: StandardizeNamesInput) -> dict:
    """
    Standardize the names in the provided FHIR bundle or resource.
    :param input: A dictionary with the schema specified by the StandardizeNamesInput
        model.
    :return: A FHIR bundle or resource with standardized names.
    """
    input = dict(input)
    return {"bundle": standardize_names(**input)}


class StandardizePhonesInput(BaseModel):
    data: dict
    overwrite: Optional[bool] = True

    _check_for_fhir = validator("data", allow_reuse=True)(check_for_fhir)


@router.post("/standardize_phones")
async def standardize_phones_endpoint(input: StandardizePhonesInput) -> dict:
    """
    Standardize the phone numbers in the provided FHIR bundle or resource.
    :param input: A dictionary with the schema specified by the StandardizePhonesInput
        model.
    :return: A FHIR bundle with standardized phone numbers.
    """
    input = dict(input)
    return {"bundle": standardize_phones(**input)}
