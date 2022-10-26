from fastapi import FastAPI
from app.routers import (
    fhir_harmonization_standardization,
    fhir_geospatial,
    fhir_linkage_link,
    fhir_transport_http,
    cloud_write_to_storage,
)
from app.config import get_settings

# Read settings immediately to fail fast in case there are invalid values.
get_settings()

# Start the API
app = FastAPI()

app.include_router(fhir_harmonization_standardization.router)
app.include_router(fhir_geospatial.router)
app.include_router(fhir_linkage_link.router)
app.include_router(fhir_transport_http.router)
app.include_router(cloud_write_to_storage.router)


@app.get("/")
async def health_check():
    return {"status": "OK"}
