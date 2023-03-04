from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Literal, Optional, Union
from pathlib import Path
from app.utils import load_extraction_schema, get_extraction_parsers


# Instantiate FastAPI and set metadata.
description = Path("description.md").read_text(encoding="utf-8")
app = FastAPI(
    title="PHDI Extraction Service",
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


# Request and respone models
class ParseMessageInput(BaseModel):
    """
    The schema for requests to the /extract endpoint.
    """

    message_format: Literal["fhir", "hl7v2", "cda"] = Field(
        description="The format of the message."
    )
    message_type: Optional[Literal["ecr", "elr", "vxu"]] = Field(
        description="The type of message that values will be extracted from."
    )
    fhir_converter_url: Optional[str] = Field(
        description="The URL of an instance of the PHDI FHIR converter to use when the "
        "message is not already in FHIR format.",
        default="",
    )
    extraction_schema: Optional[dict] = Field(
        description="A schema describing which fields to extract from the message.",
        default="",
    )
    extraction_schema_name: Optional[str] = Field(
        description="The name of a schema that was previously"
        " loaded in the service to use to extract fields from the message.",
        default="",
    )
    message: Union[str, dict] = Field(description="The message to be parsed.")


class ParseMessageResponse(BaseModel):
    """
    The schema for response from the /extract endpoint.
    """

    extracted_values: dict = Field(
        description="A set of key:value pairs containing the values extracted from the "
        "message."
    )


# Endpoints
@app.get("/")
async def health_check():
    """
    Check service status. If an HTTP 200 status code is returned along with
    '{"status": "OK"}' then the extraction service is available and running properly.
    """
    return {"status": "OK"}


@app.post("/parse_message", status_code=200)
async def parse_message_endpoint(input: ParseMessageInput) -> ParseMessageResponse:
    """
    Extract the desired values values from a message. If the message is not already in
    FHIR format convert it to FHIR first.

    :param input: A JSON formated request body with schema specified by the
        ExtractInput model.
    :return: A JSON formated response body with schema specified by the ExtractResponse
        model.
    """

    if input.extraction_schema != "":
        extraction_schema = input.extraction_schema
    elif input.extraction_schema_name != "":
        extraction_schema = load_extraction_schema(
            f"./schemas/{input.extraction_schema_name}.json"
        )
    else:
        path = Path(__file__).parent / "default_schemas" / f"{input.message_type}.json"
        extraction_schema = load_extraction_schema(path)

    parsers = get_extraction_parsers(extraction_schema)

    extracted_values = {}
    for field, parser in parsers.items():
        value = parser(input.message)
        if len(value) == 1:
            value = value[0]
        extracted_values[field] = value

    return {"extracted_values": extracted_values}