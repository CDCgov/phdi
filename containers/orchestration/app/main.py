from phdi.containers.base_service import BaseService
from fastapi import Response, status, Body
from pydantic import BaseModel, Field
from typing import Literal, Optional, Union, Annotated, Dict
from pathlib import Path
import os
from app.utils import (
    load_processing_schema,
    # get_parsers,
    # convert_to_fhir,
    # get_credential_manager,
    # search_for_required_values,
    read_json_from_assets,
    # freeze_processing_schema,
)
from app.config import get_settings
import json

# Read settings immediately to fail fast in case there are invalid values.
get_settings()

# Instantiate FastAPI via PHDI's BaseService class
app = BaseService(
    service_name="PHDI Orchestration",
    description_path=Path(__file__).parent.parent / "description.md",
).start()

# /parse_message endpoint #
process_message_request_examples = read_json_from_assets(
    "sample_parse_message_requests.json"
)
raw_process_message_response_examples = read_json_from_assets(
    "sample_parse_message_responses.json"
)
process_message_response_examples = {200: raw_process_message_response_examples}


# Request and response models
class ProcessMessageInput(BaseModel):
    """
    The schema for requests to the /extract endpoint.
    """

    credential_manager: Optional[Literal["azure", "gcp"]] = Field(
        description="The type of credential manager to use for authentication with a "
        "FHIR converter when conversion to FHIR is required.",
        default=None,
    )
    message: Union[str, dict] = Field(description="The message to be parsed.")


class ProcessMessageResponse(BaseModel):
    """
    The schema for responses from the /extract endpoint.
    """

    message: str = Field(
        description="A message describing the result of a request to "
        "the /parse_message endpoint."
    )
    processed_values: dict = Field(
        description="A set of key:value pairs containing the values extracted from the "
        "message."
    )


@app.post("/process", status_code=200, responses=process_message_response_examples)
async def process_message_endpoint(
    input: Annotated[
        ProcessMessageInput, Body(examples=process_message_request_examples)
    ],
    response: Response,
) -> ProcessMessageResponse:
    """
    Process message through a series of microservices
    """
    return {
        "message": "Processing succeeded!",
        "processed_values": process_message_response_examples,
    }


# /schemas endpoint #
raw_list_schemas_response = read_json_from_assets("sample_list_schemas_response.json")
sample_list_schemas_response = {200: raw_list_schemas_response}


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


@app.get("/schemas", responses=sample_list_schemas_response)
async def list_schemas() -> ListSchemasResponse:
    """
    Get a list of all the process schemas currently available. Default schemas are ones
    that are packaged by default with this service. Custom schemas are any additional
    schema that users have chosen to upload to this service (this feature is not yet
    implemented)
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
        "the /process endpoint."
    )
    processing_schema: dict = Field(
        description="A set of key:value pairs containing the values extracted from the "
        "message."
    )


# /schemas/{processing_schema_name} endpoint #
raw_get_schema_response = read_json_from_assets("sample_get_schema_response.json")
sample_get_schema_response = {200: raw_get_schema_response}


@app.get(
    "/schemas/{processing_schema_name}",
    status_code=200,
    responses=sample_get_schema_response,
)
async def get_schema(
    processing_schema_name: str, response: Response
) -> GetSchemaResponse:
    """
    Get the schema specified by 'processing_schema_name'.
    """
    try:
        processing_schema = load_processing_schema(processing_schema_name)
    except FileNotFoundError as error:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": error.__str__(), "processing_schema": {}}
    return {"message": "Schema found!", "processing_schema": processing_schema}


PARSING_SCHEMA_DATA_TYPES = Literal[
    "string", "integer", "float", "boolean", "date", "timestamp"
]


class ProcessingSchemaSecondaryFieldModel(BaseModel):
    fhir_path: str
    data_type: PARSING_SCHEMA_DATA_TYPES
    nullable: bool


class ProcessingSchemaFieldModel(BaseModel):
    fhir_path: str
    data_type: PARSING_SCHEMA_DATA_TYPES
    nullable: bool
    secondary_schema: Dict[str, ProcessingSchemaSecondaryFieldModel]


class ProcessingSchemaModel(BaseModel):
    processing_schema: Dict[str, ProcessingSchemaFieldModel] = Field(
        description="A JSON formatted processing schema to upload."
    )
    overwrite: Optional[bool] = Field(
        description="When `true` if a schema already exists for the provided name it "
        "will be replaced. When `false` no action will be taken and the response will "
        "indicate that a schema for the given name already exists. To proceed submit a "
        "new request with a different schema name or set this field to `true`.",
        default=False,
    )


class PutSchemaResponse(BaseModel):
    """
    The schema for responses from the /schemas endpoint when a schema is uploaded.
    """

    message: str = Field(
        "A message describing the result of a request to " "upload a processing schema."
    )


upload_schema_request_examples = read_json_from_assets(
    "sample_upload_schema_requests.json"
)

upload_schema_response_examples = {
    200: "sample_upload_schema_response.json",
    201: "sample_update_schema_response.json",
    400: "sample_upload_schema_failure_response.json",
}
for status_code, file_name in upload_schema_response_examples.items():
    upload_schema_response_examples[status_code] = read_json_from_assets(file_name)
    upload_schema_response_examples[status_code]["model"] = PutSchemaResponse


@app.put(
    "/schemas/{processing_schema_name}",
    status_code=200,
    response_model=PutSchemaResponse,
    responses=upload_schema_response_examples,
)
async def upload_schema(
    processing_schema_name: str,
    input: Annotated[
        ProcessingSchemaModel, Body(examples=upload_schema_request_examples)
    ],
    response: Response,
) -> PutSchemaResponse:
    """
    Upload a new processing schema to the service or update an existing schema.
    """

    file_path = Path(__file__).parent / "custom_schemas" / processing_schema_name
    schema_exists = file_path.exists()
    if schema_exists and not input.overwrite:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": f"A schema for the name '{processing_schema_name}' already"
            "exists. To proceed submit a new request with a different schema name or "
            "set the 'overwrite' field to 'true'."
        }

    # Convert Pydantic models to dicts so they can be serialized to JSON.
    for field in input.processing_schema:
        input.processing_schema[field] = input.processing_schema[field].dict()

    with open(file_path, "w") as file:
        json.dump(input.processing_schema, file, indent=4)

    if schema_exists:
        return {"message": "Schema updated successfully!"}
    else:
        response.status_code = status.HTTP_201_CREATED
        return {"message": "Schema uploaded successfully!"}
