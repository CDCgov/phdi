from pathlib import Path
from typing import Annotated

import httpx
from dibbs.base_service import BaseService
from fastapi import Query
from fastapi import Request
from fastapi import Response
from fastapi import status
from fastapi.openapi.utils import get_openapi
from fastapi.responses import FileResponse

from app.config import get_settings
from app.models import RefineECRResponse
from app.refine import refine
from app.refine import validate_message
from app.refine import validate_sections_to_include
from app.utils import create_clinical_xpaths
from app.utils import read_json_from_assets

settings = get_settings()
TCR_ENDPOINT = f"{settings['tcr_url']}/get-value-sets?condition_code="


# Instantiate FastAPI via DIBBs' BaseService class
app = BaseService(
    service_name="Message Refiner",
    service_path="/message-refiner",
    description_path=Path(__file__).parent.parent / "description.md",
    include_health_check_endpoint=False,
    openapi_url="/message-refiner/openapi.json",
).start()


# /ecr endpoint request examples
refine_ecr_request_examples = read_json_from_assets("sample_refine_ecr_request.json")
refine_ecr_response_examples = read_json_from_assets("sample_refine_ecr_response.json")


def custom_openapi():
    """
    This customizes the FastAPI response to allow example requests given that the
    raw Request cannot have annotations.
    """
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    path = openapi_schema["paths"]["/ecr"]["post"]
    path["requestBody"] = {
        "content": {
            "application/xml": {
                "schema": {"type": "Raw eCR XML payload"},
                "examples": refine_ecr_request_examples,
            }
        }
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/")
async def health_check():
    """
    Check service status. If an HTTP 200 status code is returned along with
    '{"status": "OK"}' then the refiner service is available and running
    properly.
    """
    return {"status": "OK"}


@app.get("/example-collection")
async def get_uat_collection() -> FileResponse:
    """
    Fetches a Postman Collection of sample requests designed for UAT.
    The Collection is a JSON-exported file consisting of five GET and POST
    requests to endpoints of the publicly available dibbs.cloud server.
    The requests showcase the functionality of various aspects of the TCR
    and the message refine.
    """
    uat_collection_path = (
        Path(__file__).parent.parent
        / "assets"
        / "Message_Refiner_UAT.postman_collection.json"
    )
    return FileResponse(
        path=uat_collection_path,
        media_type="application/json",
        filename="Message_Refiner_Postman_Samples.json",
    )


@app.post(
    "/ecr",
    response_model=RefineECRResponse,
    status_code=200,
    responses=refine_ecr_response_examples,
)
async def refine_ecr(
    refiner_input: Request,
    sections_to_include: Annotated[
        str | None,
        Query(
            description="""The sections of an ECR to include in the refined message.
            Multiples can be delimited by a comma. Valid LOINC codes for sections are:\n
            46240-8: Encounters--Hospitalizations+outpatient visits narrative\n
            10164-2: History of present illness\n
            11369-6: History of immunizations\n
            29549-3: Medications administered\n
            18776-5: Plan of treatment: Care plan\n
            11450-4: Problem--Reported list\n
            29299-5: Reason for visit\n
            30954-2: Results--Diagnostic tests/laboratory data narrative\n
            29762-2: Social history--Narrative\n
            """
        ),
    ] = None,
    conditions_to_include: Annotated[
        str | None,
        Query(
            description="The SNOMED condition codes to use to search for relevant clinical services in the ECR."
            + " Multiples can be delimited by a comma."
        ),
    ] = None,
) -> Response:
    """
    Refines an incoming XML ECR message based on sections to include and/or trigger code
    conditions to include, based on the parameters included in the endpoint.

    The return will be a formatted, refined XML, limited to just the data specified.

    :param refiner_input: The request object containing the XML input.
    :param sections_to_include: The fields to include in the refined message.
    :param conditions_to_include: The SNOMED condition codes to use to search for
    relevant clinical services in the ECR.
    :return: The RefineECRResponse, the refined XML as a string.
    """
    data = await refiner_input.body()

    validated_message, error_message = validate_message(data)
    if error_message:
        return Response(content=error_message, status_code=status.HTTP_400_BAD_REQUEST)

    sections = None
    if sections_to_include:
        sections, error_message = validate_sections_to_include(sections_to_include)
        if error_message:
            return Response(
                content=error_message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

    clinical_services_xpaths = None
    if conditions_to_include:
        responses = await get_clinical_services(conditions_to_include)
        # confirm all API responses were 200
        if set([response.status_code for response in responses]) != {200}:
            error_message = ";".join(
                [str(response) for response in responses if response.status_code != 200]
            )
            return Response(
                content=error_message, status_code=status.HTTP_502_BAD_GATEWAY
            )
        clinical_services = [response.json() for response in responses]
        clinical_services_xpaths = create_clinical_xpaths(clinical_services)

    data = refine(validated_message, sections, clinical_services_xpaths)

    return Response(content=data, media_type="application/xml")


async def get_clinical_services(condition_codes: str) -> list[dict]:
    """
    This a function that loops through the provided condition codes. For each
    condition code provided, it calls the trigger-code-reference service to get
    the API response for that condition.

    :param condition_codes: SNOMED condition codes to look up in TCR service
    :return: List of API responses to check
    """
    clinical_services_list = []
    conditions_list = condition_codes.split(",")
    async with httpx.AsyncClient() as client:
        for condition in conditions_list:
            response = await client.get(TCR_ENDPOINT + condition)
            clinical_services_list.append(response)
    return clinical_services_list
