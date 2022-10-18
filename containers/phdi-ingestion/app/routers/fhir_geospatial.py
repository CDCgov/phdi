import os
from fastapi import APIRouter, Response, status
from pydantic import BaseModel, validator
from phdi.fhir.geospatial import SmartyFhirGeocodeClient, CensusFhirGeocodeClient
from app.utils import check_for_environment_variables, check_for_fhir_bundle


router = APIRouter(
    prefix="/fhir/geospatial/geocode",
    tags=["fhir/geospatial"],
)


class GeocodeAddressInBundleInput(BaseModel):
    bundle: dict
    geocode_method: str = ""
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

    If the geocode method is smarty then the auth_id and auth_token parameter
    values will be used.  If they are not provided in the request then the values
    will be obtained via environment variables.  In the case where smarty is the geocode 
    method and auth_id and auth_token are not supplied an HTTP 500 status code will
    be returned.
    :param input: A JSON formated request body with schema specified by the
        GeocodeAddressInBundleInput model.
    :return: A FHIR bundle where every patient resource address will now contain a geocoded value.
    """

    input = dict(input)

    if input.get("geocode_method") in [None, ""]:
        check_result = check_for_environment_variables(["geocode_method"])
        if check_result["status_code"] == 500:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return check_result
        else:
            input["geocode_method"] = os.environ.get("geocode_method")

    if input.get("geocode_method") == "smarty":
        if input.get("auth_id") in [None,""]:
            check_result = check_for_environment_variables(["auth_id"])
            if check_result["status_code"] == 500:
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                return check_result
            else:
                input["auth_id"] = os.environ.get("auth_id")
        if input.get("auth_token") in [None,""]:
            check_result = check_for_environment_variables(["auth_token"])
            if check_result["status_code"] == 500:
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                return check_result
            else:
                input["auth_token"] = os.environ.get("auth_token")
        geocode_client = SmartyFhirGeocodeClient(auth_id=input.get("auth_id"),auth_token=input.get("auth_token"))
    elif input.get("geocode_method") == "census":
        geocode_client = CensusFhirGeocodeClient()
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        response.message = "Invalid Geocode Method selected!"
        return response


    return geocode_client.geocode_bundle(**input)


