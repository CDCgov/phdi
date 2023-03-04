from fastapi import FastAPI
from pydantic import BaseModel, Field, root_validator
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
        description="The type of message that values will be extracted from. Required "
        "when 'message_format is not FHIR."
    )
    fhir_converter_url: Optional[str] = Field(
        description="The URL of an instance of the PHDI FHIR converter. Required when "
        "the message is not already in FHIR format.",
        default="",
    )
    parsing_schema: Optional[dict] = Field(
        description="A schema describing which fields to extract from the message.",
        default={},
    )
    parsing_schema_name: Optional[str] = Field(
        description="The name of a schema that was previously"
        " loaded in the service to use to extract fields from the message.",
        default="",
    )
    message: Union[str, dict] = Field(description="The message to be parsed.")

    @root_validator
    def require_message_type_when_not_fhir(cls, values):
        if (
            values.get("message_format") != "fhir"
            and values.get("message_type") is None
        ):
            raise ValueError(
                "When the message format is not FHIR then the message type must be included."
            )
        return values

    @root_validator
    def prohibit_schema_and_schema_name(cls, values):
        if (
            values.get("parsing_schema") != {}
            and values.get("parsing_schema_name") != ""
        ):
            raise ValueError(
                "Values for both 'parsing_schema' and 'parsing_schema_name' have been "
                "provided. Only one of these values is permited"
            )
        return values

    @root_validator
    def require_schema_or_schema_name(cls, values):
        if (
            values.get("parsing_schema") == {}
            and values.get("parsing_schema_name") == ""
        ):
            raise ValueError(
                "Values for 'parsing_schema' and 'parsing_schema_name' have not been "
                "provided. One, but not both, of these values is required. "
            )
        return values


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

    if input.parsing_schema != {}:
        extraction_schema = input.parsing_schema
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
