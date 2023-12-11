from pathlib import Path

from dibbs.containers.base_service import BaseService
from pydantic import BaseModel, Field

from app.config import get_settings


# read settings immediately to fail fast in case there are invalid values.
get_settings()

# instantiate FastAPI via PHDI's BaseService class
# TODO:
# - this should be the only place where `phdi` is imported in this container
# - at a later point, we will import this from a non-SDK source, e.g., a dibbs
#   library with only util functions that are building block agnostic and provide
#   true utility to our services
app = BaseService(
    service_name="DIBBs Ingestion Service",
    description_path=Path(__file__).parent.parent / "description.md",
).start()


class StandardizeInput(BaseModel):
    """
    A request model for the standardize endpoint.
    """

    unstandardized: str


class StandardizeResponse(BaseModel):
    """
    A response model for the standardize endpoint.
    """

    standardized: str


class HealthCheckResponse(BaseModel):
    """
    The schema for response from the Standardization health check endpoint.
    """

    status: str = Field(description="Returns status of this service")


@app.get("/")
async def health_check() -> HealthCheckResponse:
    """
    A health check endpoint for the service.
    """
    return {"status": "OK"}
