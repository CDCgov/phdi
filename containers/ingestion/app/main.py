from phdi.containers.base_service import BaseService
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

# Instantiate FastAPI via PHDI's BaseService class
app = BaseService(
    service_name="PHDI Ingestion Service",
    description_path=Path(__file__).parent.parent / "description.md",
).start()

app.include_router(fhir_harmonization_standardization.router)
app.include_router(fhir_geospatial.router)
app.include_router(fhir_linkage_link.router)
app.include_router(fhir_transport_http.router)
app.include_router(cloud_storage.router)
