from fastapi import APIRouter

router = APIRouter(
    prefix="/fhir/transport/http",
    tags=["fhir/transport"],
)


@router.post("/upload_bundle")
async def upload_bundle_endpoint(body):
    return body
