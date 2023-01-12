from fastapi import APIRouter, Response, status
from pydantic import BaseModel, validator
from typing import Optional, Literal
from phdi.fhir.geospatial import SmartyFhirGeocodeClient, CensusFhirGeocodeClient
from app.utils import (
    search_for_required_values,
    check_for_fhir_bundle,
    StandardResponse,
)


router = APIRouter(
    prefix="/fhir/geospatial/geocode",
    tags=["fhir/geospatial"],
)


class GeocodeAddressInBundleInput(BaseModel):
    bundle: dict
    geocode_method: Literal["smarty", "census"]
    auth_id: Optional[str] = ""
    auth_token: Optional[str] = ""
    overwrite: Optional[bool] = True

    _check_for_fhir = validator("bundle", allow_reuse=True)(check_for_fhir_bundle)


@router.post("/geocode_bundle", status_code=200)
def geocode_bundle_endpoint(
    input: GeocodeAddressInBundleInput, response: Response
) -> StandardResponse:
    """
    Given a FHIR bundle and a specified geocode method, with any required
    subsequent credentials (ie.. SmartyStreets auth id and auth token),
    geocode all patient addresses across all patient resources in the bundle.

    If the geocode method is smarty then the auth_id and auth_token parameter
    values will be used.  If they are not provided in the request then the values
    will be obtained via environment variables.  In the case where smarty is the geocode
    method and auth_id and/or auth_token are not supplied then an HTTP 400 status
    code will be returned.
    :param input: A JSON formated request body with schema specified by the
        GeocodeAddressInBundleInput model.
    :return: A FHIR bundle where every patient resource address will now
    contain a geocoded value.
    """

    input = dict(input)

    if input.get("geocode_method") == "smarty":
        required_values = ["auth_id", "auth_token"]
        search_result = search_for_required_values(input, required_values)
        if search_result != "All values were found.":
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"status_code": 400, "message": search_result}
        geocode_client = SmartyFhirGeocodeClient(
            auth_id=input.get("auth_id"), auth_token=input.get("auth_token")
        )

    elif input.get("geocode_method") == "census":
        geocode_client = CensusFhirGeocodeClient()

    # Here we need to remove the parameters that are used here
    #   but are not required in the PHDI function in the SDK
    input.pop("geocode_method", None)
    input.pop("auth_id", None)
    input.pop("auth_token", None)
    try:
        result = geocode_client.geocode_bundle(**input)
    except Exception as error:
        response.status_code = status.HTTP_400_BAD_REQUEST
        result = {"error": error}
    return {"status_code": "200", "bundle": result}
