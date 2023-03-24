from fastapi import FastAPI
from app.routers import (
    fhir_harmonization_standardization,
    fhir_geospatial,
    fhir_linkage_link,
    fhir_transport_http,
    cloud_storage,
)
from app.config import get_settings
from containers.utils import instantiate_fastapi

# Read settings immediately to fail fast in case there are invalid values.
get_settings()

# Instantiate FastAPI and set metadata.
app = instantiate_fastapi("PHDI Ingestion Service", "0.0.1")

app.include_router(fhir_harmonization_standardization.router)
app.include_router(fhir_geospatial.router)
app.include_router(fhir_linkage_link.router)
app.include_router(fhir_transport_http.router)
app.include_router(cloud_storage.router)


@app.get("/")
async def health_check():
    return {"status": "OK"}
