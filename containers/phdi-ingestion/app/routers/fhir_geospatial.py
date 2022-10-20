import json
import os
from fastapi import APIRouter, Response, status
from pydantic import BaseModel, validator
from typing import Optional, Literal
from phdi.fhir.geospatial import SmartyFhirGeocodeClient, CensusFhirGeocodeClient
from app.utils import search_for_required_values, check_for_fhir_bundle


router = APIRouter(
    prefix="/fhir/geospatial/geocode",
    tags=["fhir/geospatial"],
)


class GeocodeAddressInBundleInput(BaseModel):
    bundle: dict
    geocode_method: Literal["smarty", "census", "all"]
    auth_id: Optional[str] = ""
    auth_token: Optional[str] = ""
    overwrite: Optional[bool] = True

    _check_for_fhir = validator("bundle", allow_reuse=True)(check_for_fhir_bundle)


@router.post("/geocode_bundle", status_code=200)
async def geocode_bundle_endpoint(input: GeocodeAddressInBundleInput, response: Response)->dict:
    """
    Given a FHIR bundle and a specified geocode method, with any required
    subsequent credentials (ie.. SmartyStreets auth id and auth token),
    geocode all patient addresses across all patient resources in the bundle.

    If the geocode method is smarty or all, then the auth_id and auth_token parameter
    values will be used.  If they are not provided in the request then the values
    will be obtained via environment variables.  In the case where smarty is the geocode 
    method and auth_id and auth_token are not supplied an HTTP 500 status code will
    be returned.
    :param input: A JSON formated request body with schema specified by the
        GeocodeAddressInBundleInput model.
    :return: A FHIR bundle where every patient resource address will now contain a geocoded value.
    """

    input = dict(input)
    
    if input.get("geocode_method") in ["smarty","all"]:
        required_values = ["auth_id", "auth_token"]
        search_result = search_for_required_values(input, required_values)
        if search_result != "All values were found.":
            response.status_code = status.HTTP_400_BAD_REQUEST
            return search_result
        geocode_client = SmartyFhirGeocodeClient(auth_id=input.get("auth_id"),auth_token=input.get("auth_token"))
    
    if input.get("geocode_method") in ["census","all"]:
        geocode_client = CensusFhirGeocodeClient()

    if input.get("geocode_method") not in ["smarty","census","all"]:
        response.status_code = status.HTTP_400_BAD_REQUEST
        response.message = "Invalid Geocode Method selected!"
        return response

    # Here we need to remove the parameters that are used here
    #   but are not required in the PHDI function in the SDK
    del input['geocode_method']
    del input['auth_id']
    del input['auth_token']

    return geocode_client.geocode_bundle(**input)
