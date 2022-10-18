from fastapi import FastAPI
from app.routers import (
    fhir_harmonization_standardization,
    fhir_geospatial,
    fhir_linkage_link,
    fhir_transport_http,
)

app = FastAPI()

app.include_router(fhir_harmonization_standardization.router)
app.include_router(fhir_geospatial.router)
app.include_router(fhir_linkage_link.router)
app.include_router(fhir_transport_http.router)


@app.get("/")
async def health_check():
    return {"status": "OK"}
