from fastapi import APIRouter
from phdi.fhir.linkage.link import add_patient_identifier

router = APIRouter(
    prefix="/fhir/linkage/link",
    tags=["fhir/linkage"],
)


@router.post("/add_patient_identifier")
async def add_patient_identifier_endpoint(body):
    return body
