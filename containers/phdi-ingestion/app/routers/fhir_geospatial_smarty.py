from fastapi import APIRouter
from phdi.geo import get_smartystreets_client, geocode_patients

router = APIRouter(
    prefix="/fhir/geospatial/smarty",
    tags=["fhir/geospatial"],
)


@router.post("/geocode_bundle")
async def geocode_bundle_endpoint(body):
    return body
