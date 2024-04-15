from dibbs.base_service import BaseService
from pathlib import Path


# Instantiate FastAPI via DIBBs' BaseService class
app = BaseService(
    service_name="eCR Refiner",
    service_path="/refiner",
    description_path=Path(__file__).parent.parent / "description.md",
    include_health_check_endpoint=False,
).start()


@app.get("/")
async def health_check():
    """
    Check service status. If an HTTP 200 status code is returned along with
    '{"status": "OK"}' then the refiner service is available and running
    properly.
    """
    return {"status": "OK"}
