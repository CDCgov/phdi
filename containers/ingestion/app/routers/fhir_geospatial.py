from typing import Annotated
from typing import Literal
from typing import Optional

from fastapi import APIRouter
from fastapi import Body
from fastapi import Response
from fastapi import status
from pydantic import BaseModel
from pydantic import Field
from pydantic import validator

from app.config import get_settings
from app.fhir.geospatial import CensusFhirGeocodeClient
from app.fhir.geospatial import SmartyFhirGeocodeClient
from app.utils import check_for_fhir_bundle
from app.utils import read_json_from_assets
from app.utils import search_for_required_values
from app.utils import StandardResponse

router = APIRouter(
    prefix="/fhir/geospatial/geocode",
    tags=["fhir/geospatial"],
)

license_types = Literal[
    "us-standard-cloud",
    "us-core-cloud",
    "us-rooftop-geocoding-cloud",
    "us-rooftop-geocoding-enterprise-cloud",
    "us-autocomplete-pro-cloud",
    "international-global-plus-cloud",
]

# Sample request/response for the geocode endpoint
geocode_request_examples = read_json_from_assets("sample_geocode_request_data.json")

raw_geocode_response_data = read_json_from_assets("sample_geocode_responses.json")

sample_geocode_response = {200: raw_geocode_response_data}


class GeocodeAddressInBundleInput(BaseModel):
    bundle: dict = Field(description="A FHIR resource or bundle in JSON format.")
    geocode_method: Literal["smarty", "census"] = Field(
        description="The geocoding service to be used."
    )
    smarty_auth_id: Optional[str] = Field(
        description="Authentication ID for the geocoding service. Must be provided in "
        "the request body or set as an environment variable of the "
        "service if "
        "`geocode_method` is `smarty`.",
        default="",
    )
    smarty_auth_token: Optional[str] = Field(
        description="Authentication Token for the geocoding service. Must be provided "
        "in the request body or set as an environment variable of the "
        "service if "
        "`geocode_method` is `smarty`.",
        default="",
    )
    license_type: Optional[license_types] = Field(
        description="License type for the geocoding service. Must be provided "
        "in the request body or set as an environment variable of the "
        "service if "
        "`geocode_method` is `smarty`.",
        default="us-rooftop-geocoding-enterprise-cloud",
    )
    overwrite: Optional[bool] = Field(
        description="If true, `data` is modified in-place; if false, a copy of `data` "
        "modified and returned.",
        default=True,
    )

    _check_for_fhir = validator("bundle", allow_reuse=True)(check_for_fhir_bundle)


@router.post("/geocode_bundle", status_code=200, responses=sample_geocode_response)
def geocode_bundle_endpoint(
    input: Annotated[
        GeocodeAddressInBundleInput, Body(examples=geocode_request_examples)
    ],
    response: Response,
) -> StandardResponse:
    """
    Given a FHIR bundle and a specified geocoding method, this endpoint
    geocodes all patient addresses across all patient resources in the bundle.

    Two geocoding methods are currently supported — Smarty and the U.S. Census.

    If using the Smarty provider, the request parameter: smarty_auth_id,
    smarty_auth_token and license_type must be provided. If they aren't
    provided as request parameters, then the service will attempt to obtain
    them through environment variables. If they can’t be found in either the
    request parameters or environment variables, an HTTP 400 status will be
    returned.
    """
    input = dict(input)

    if input.get("geocode_method") == "smarty":
        required_values = ["smarty_auth_id", "smarty_auth_token"]
        search_result = search_for_required_values(input, required_values)
        if search_result != "All values were found.":
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"status_code": 400, "message": search_result}
        license_type = input.get("license_type") or get_settings().get("license_type")
        if license_type:
            geocode_client = SmartyFhirGeocodeClient(
                smarty_auth_id=input.get("smarty_auth_id"),
                smarty_auth_token=input.get("smarty_auth_token"),
                licenses=[license_type],
            )
        else:
            geocode_client = SmartyFhirGeocodeClient(
                smarty_auth_id=input.get("smarty_auth_id"),
                smarty_auth_token=input.get("smarty_auth_token"),
            )

    elif input.get("geocode_method") == "census":
        geocode_client = CensusFhirGeocodeClient()

    # Here we need to remove the parameters that are used here
    #   but are not required in the PHDI function in the SDK
    input.pop("geocode_method", None)
    input.pop("smarty_auth_id", None)
    input.pop("smarty_auth_token", None)
    input.pop("license_type", None)
    result = {}
    try:
        geocoder_result = geocode_client.geocode_bundle(**input)
        result["status_code"] = "200"
        result["bundle"] = geocoder_result
    except Exception as error:
        response.status_code = status.HTTP_400_BAD_REQUEST
        geocoder_result = "Smarty raised the following exception: " + error.__str__()
        result["status_code"] = "400"
        result["message"] = geocoder_result

    return result
