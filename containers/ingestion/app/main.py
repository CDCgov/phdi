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

# Instantiate FastAPI and set metadata.
description = Path("description.md").read_text(encoding="utf-8")
app = FastAPI(
    title="PHDI Ingestion Service",
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
    description=description,
)

app.include_router(fhir_harmonization_standardization.router)
app.include_router(fhir_geospatial.router)
app.include_router(fhir_linkage_link.router)
app.include_router(fhir_transport_http.router)
app.include_router(cloud_storage.router)


@app.get("/")
async def health_check():
    return {"status": "OK"}
