from fastapi import FastAPI
from app.routers import (
    fhir_harmonization_standardization,
    fhir_geospatial,
    fhir_linkage_link,
    fhir_transport_http,
    cloud_storage,
)
from app.config import get_settings
from pathlib import Path

# Read settings immediately to fail fast in case there are invalid values.
get_settings()

# Start the API and set service metadata.
description = Path('getting-started.md').read_text()
app = FastAPI(
    title="PHDI Ingestion Service",
    description=description,
    version="0.0.1",
    contact={
        "name": "CDC Public Health Data Infrastructure",
        "url": "https://cdcgov.github.io/phdi-site/",
        "email": "dmibuildingblocks@cdc.gov",
    },
    license_info={
        "name": "Creative Commons Zero v1.0 Universal",
        "url": "https://creativecommons.org/publicdomain/zero/1.0/",
    },
)

# Include endpoints.
app.include_router(fhir_harmonization_standardization.router)
app.include_router(fhir_geospatial.router)
app.include_router(fhir_linkage_link.router)
app.include_router(fhir_transport_http.router)
app.include_router(cloud_storage.router)


@app.get("/")
async def health_check():
    return {"status": "OK"}
