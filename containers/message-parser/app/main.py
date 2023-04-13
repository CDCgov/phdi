from fastapi import FastAPI, Response, status
from pydantic import BaseModel, Field, root_validator
from typing import Literal, Optional, Union
from pathlib import Path
from frozendict import frozendict
import os
from app.utils import (
    load_parsing_schema,
    get_parsers,
    convert_to_fhir,
    get_credential_manager,
    search_for_required_values,
)
from app.config import get_settings

# Read settings immediately to fail fast in case there are invalid values.
get_settings()

# Instantiate FastAPI and set metadata.
description = Path("description.md").read_text(encoding="utf-8")
app = FastAPI(
    title="PHDI Message Parser",
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


# /health_check endpoint #
@app.get("/")
async def health_check():
    """
    Check service status. If an HTTP 200 status code is returned along with
    '{"status": "OK"}' then the extraction service is available and running properly.
    """
    return {"status": "OK"}


# /parse_message endpoint #


# Request and response models
class ParseMessageInput(BaseModel):
    """
    The schema for requests to the /extract endpoint.
    """

    message_format: Literal["fhir", "hl7v2", "ecr"] = Field(
        description="The format of the message."
    )
    message_type: Optional[Literal["ecr", "elr", "vxu"]] = Field(
        description="The type of message that values will be extracted from. Required "
        "when 'message_format is not FHIR."
    )
    parsing_schema: Optional[dict] = Field(
        description="A schema describing which fields to extract from the message. This"
        " must be a JSON object with key:value pairs of the form "
        "<my-field>:<FHIR-to-my-field>.",
        default={},
    )
    parsing_schema_name: Optional[str] = Field(
        description="The name of a schema that was previously"
        " loaded in the service to use to extract fields from the message.",
        default="",
    )
    fhir_converter_url: Optional[str] = Field(
        description="The URL of an instance of the PHDI FHIR converter. Required when "
        "the message is not already in FHIR format.",
        default="",
    )
    credential_manager: Optional[Literal["azure", "gcp"]] = Field(
        description="The type of credential manager to use for authentication with a "
        "FHIR converter when conversion to FHIR is required.",
        default=None,
    )
    message: Union[str, dict] = Field(description="The message to be parsed.")

    @root_validator
    def require_message_type_when_not_fhir(cls, values):
        if (
            values.get("message_format") != "fhir"
            and values.get("message_type") is None
        ):
            raise ValueError(
                "When the message format is not FHIR then the message type must be "
                "included."
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
                "provided. Only one of these values is permited."
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
                "provided. One, but not both, of these values is required."
            )
        return values


class ParseMessageResponse(BaseModel):
    """
    The schema for responses from the /extract endpoint.
    """

    message: str = Field(
        description="A message describing the result of a request to "
        "the /parse_message endpoint."
    )
    parsed_values: dict = Field(
        description="A set of key:value pairs containing the values extracted from the "
        "message."
    )


@app.post("/parse_message", status_code=200)
async def parse_message_endpoint(
    input: ParseMessageInput, response: Response
) -> ParseMessageResponse:
    """
    Extract the desired values from a message. If the message is not already in
    FHIR format convert it to FHIR first.

    :param input: A JSON formated request body with schema specified by the
        ParseMessageInput model.
    :return: A JSON formated response body with schema specified by the
        ParseMessageResponse model.
    """
    # 1. Load schema.
    if input.parsing_schema != {}:
        parsing_schema = input.parsing_schema
    else:
        try:
            parsing_schema = load_parsing_schema(input.parsing_schema_name)
        except FileNotFoundError as error:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message": error.__str__(), "parsed_values": {}}

    # 2. Convert to FHIR, if necessary.
    if input.message_format != "fhir":
        if input.credential_manager is not None:
            input.credential_manager = get_credential_manager(
                credential_manager=input.credential_manager,
                location_url=input.fhir_converter_url,
            )

        search_result = search_for_required_values(dict(input), ["fhir_converter_url"])
        if search_result != "All values were found.":
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message": search_result, "parsed_values": {}}

        fhir_converter_response = convert_to_fhir(
            message=input.message,
            message_type=input.message_type,
            fhir_converter_url=input.fhir_converter_url,
            credential_manager=input.credential_manager,
        )
        if fhir_converter_response.status_code == 200:
            input.message = fhir_converter_response.json()["FhirResource"]
        else:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                "message": f"Failed to convert to FHIR: {fhir_converter_response.text}",
                "parsed_values": {},
            }

    # 3. Generate parsers for FHIRpaths specified in schema.
    parsers = get_parsers(frozendict(parsing_schema))

    # 4. Extract desired fields from message by applying each parser.
    parsed_values = {}
    for field, parser in parsers.items():
        value = parser(input.message)
        if len(value) == 1:
            value = value[0]
        parsed_values[field] = value

    return {"message": "Parsing succeeded!", "parsed_values": parsed_values}


# /schemas endpoint #
class ListSchemasResponse(BaseModel):
    """
    The schema for responses from the /schemas endpoint.
    """

    default_schemas: list = Field(
        description="The schemas that ship with with this service by default."
    )
    custom_schemas: list = Field(
        description="Additional schemas that users have uploaded to this service beyond"
        " the ones come by default."
    )


@app.get("/schemas", status_code=200)
async def list_schemas() -> ListSchemasResponse:
    """
    Get a list of all the parsing schemas currently available. Default schemas are ones
    that are packaged by default with this service. Custom schemas are any additional
    schema that users have chosen to upload to this service.

    :return: A JSON formated response body with schema specified by the
        ListSchemasResponse model.
    """
    default_schemas = os.listdir(Path(__file__).parent / "default_schemas")
    custom_schemas = os.listdir(Path(__file__).parent / "custom_schemas")
    custom_schemas = [schema for schema in custom_schemas if schema != ".keep"]
    schemas = {"default_schemas": default_schemas, "custom_schemas": custom_schemas}
    return schemas


class GetSchemaResponse(BaseModel):
    """
    The schema for responses from the /schemas endpoint when a specific schema is
    queried.
    """

    message: str = Field(
        description="A message describing the result of a request to "
        "the /parse_message endpoint."
    )
    parsing_schema: dict = Field(
        description="A set of key:value pairs containing the values extracted from the "
        "message."
    )


@app.get("/schemas/{parsing_schema_name}", status_code=200)
async def get_schema(parsing_schema_name: str, response: Response) -> GetSchemaResponse:
    """
    Get the schema specified by 'parsing_schema_name'.

    :return: A JSON formated response body with schema specified by the
        GetSchemaResponse model.
    """
    try:
        parsing_schema = load_parsing_schema(parsing_schema_name)
    except FileNotFoundError as error:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": error.__str__(), "parsing_schema": {}}
    return {"message": "Schema found!", "parsing_schema": parsing_schema}
