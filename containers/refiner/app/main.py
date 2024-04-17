from pathlib import Path

from dibbs.base_service import BaseService

from app.models import RefinerInput
from app.models import RefinerResponse


# Instantiate FastAPI via DIBBs' BaseService class
app = BaseService(
    service_name="Message Refiner",
    service_path="/message-refiner",
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


@app.post("/ecr")
async def refine_ecr(refiner_input: RefinerInput):
    """
    Refines an incoming XML message based on the fields to include and whether
    to include headers.

    :param request: The request object containing the XML input.
    :return: The RefinerResponse which includes the `refined_message`
    """
    return RefinerResponse(refined_message=refiner_input.message)
