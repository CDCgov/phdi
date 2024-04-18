from pathlib import Path


from dibbs.base_service import BaseService
from fastapi import Response, Request

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


@app.post("/ecr/")
async def refine_ecr(
    refiner_input: Request, sections_to_include: str | None = None
) -> Response:
    """
    Refines an incoming XML message based on the fields to include and whether
    to include headers.

    :param request: The request object containing the XML input.
    :param fields_to_include: The fields to include in the refined message.
    :return: The RefinerResponse which includes the `refined_message`
    """
    data = await refiner_input.body()

    if sections_to_include:
        # TODO: add logic to filter the XML message based on the sections to include
        refined_message = Response(content=data, media_type="application/xml")
    else:
        refined_message = Response(content=data, media_type="application/xml")

    return refined_message
