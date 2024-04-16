from pathlib import Path

from dibbs.base_service import BaseService
from app.models import RefinerInput, RefinerResponse

from app.models import RefinerInput
from app.models import RefinerResponse

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


@app.post("/refine-ecr")
async def refine_ecr(
    input: RefinerInput,
) -> RefinerResponse:
    """
    Refines an incoming XML message based on the fields to include and whether
    to include headers.

    :param input: The input to the refiner service.
    :return: The RefinerResponse which includes the `refined_message` and a
    `status`.
    """
    return RefinerResponse(refined_message=input.message, status="OK")
