from pathlib import Path

from phdi.containers.base_service import BaseService

from app.config import get_settings
from app.models import HealthCheckResponse

# read settings immediately to fail fast in case there are invalid values.
get_settings()

# instantiate FastAPI via PHDI's BaseService class
# TODO:
# - this should be the only place where `phdi` is imported in this container
# - at a later point, we will import this from a non-SDK source, e.g., a dibbs
#   library with only util functions that are building block agnostic and provide
#   true utility to our services
app = BaseService(
    service_name="DIBBs Standardization Service",
    description_path=Path(__file__).parent.parent / "description.md",
).start()


@app.get("/")
async def health_check() -> HealthCheckResponse:
    """
    A health check endpoint for the service.
    """
    return {"status": "OK"}
