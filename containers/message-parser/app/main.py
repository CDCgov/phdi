import json
import os
from pathlib import Path
from typing import Annotated

from app.config import get_settings
from app.models import FhirToPhdcInput
from app.models import GetSchemaResponse
from app.models import ListSchemasResponse
from app.models import ParseMessageInput
from app.models import ParseMessageResponse
from app.models import ParsingSchemaModel
from app.models import PutSchemaResponse
from app.phdc.builder import PHDCBuilder
from app.utils import convert_to_fhir
from app.utils import extract_and_apply_parsers
from app.utils import freeze_parsing_schema
from app.utils import get_credential_manager
from app.utils import get_metadata
from app.utils import load_parsing_schema
from app.utils import read_json_from_assets
from app.utils import search_for_required_values
from app.utils import transform_to_phdc_input_data
from fastapi import Body
from fastapi import Response
from fastapi import status

from phdi.containers.base_service import BaseService


# Read settings immediately to fail fast in case there are invalid values.
get_settings()

# Instantiate FastAPI via PHDI's BaseService class
app = BaseService(
    service_name="PHDI Message Parser",
    service_path="/message-parser",
    description_path=Path(__file__).parent.parent / "description.md",
).start()

# /parse_message endpoint #
parse_message_request_examples = read_json_from_assets(
    "sample_parse_message_requests.json"
)
raw_parse_message_response_examples = read_json_from_assets(
    "sample_parse_message_responses.json"
)
parse_message_response_examples = {200: raw_parse_message_response_examples}


@app.get("/")
async def health_check():
    """
    Check service status. If an HTTP 200 status code is returned along with
    '{"status": "OK"}' then the FHIR conversion service is available and running
    properly.
    """
    return {"status": "OK"}


@app.post("/parse_message", status_code=200, responses=parse_message_response_examples)
async def parse_message_endpoint(
    input: Annotated[ParseMessageInput, Body(examples=parse_message_request_examples)],
    response: Response,
) -> ParseMessageResponse:
    """
    Extract the desired values from a message. If the message is not already in
    FHIR format, convert it to FHIR first. You can either provide a parsing schema
    or the name of a previously loaded parsing schema.
    """
    # 1. Load schema.
    if input.parsing_schema != {}:
        parsing_schema = freeze_parsing_schema(input.parsing_schema)
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

    # 3. Parse the desired values and find metadata, if needed
    parsed_values = extract_and_apply_parsers(parsing_schema, input.message, response)
    if input.include_metadata == "true":
        parsed_values = get_metadata(parsed_values, parsing_schema)
    return {"message": "Parsing succeeded!", "parsed_values": parsed_values}


# /fhir_to_phdc endpoint #
fhir_to_phdc_request_examples = read_json_from_assets(
    "sample_fhir_to_phdc_requests.json"
)
raw_fhir_to_phdc_response_examples = read_json_from_assets(
    "sample_fhir_to_phdc_response.json"
)
fhir_to_phdc_response_examples = {200: raw_fhir_to_phdc_response_examples}


@app.post("/fhir_to_phdc", status_code=200, responses=fhir_to_phdc_response_examples)
async def fhir_to_phdc_endpoint(
    input: Annotated[FhirToPhdcInput, Body(examples=fhir_to_phdc_request_examples)],
    response: Response,
):
    """
    Convert a FHIR bundle to a Public Health Document Container (PHDC).
    """

    # 1. Identify the parsing schema based on the supplied phdc type
    match input.phdc_report_type:
        case "case_report":
            parsing_schema = load_parsing_schema("phdc_case_report_schema.json")
        case "contact_record":
            pass
        case "lab_report":
            pass
        case "morbidity_report":
            pass

    # 2. Extract data from FHIR
    parsed_values = extract_and_apply_parsers(parsing_schema, input.message, response)

    # 3. Transform to PHDCbuilder data classes
    input_data = transform_to_phdc_input_data(parsed_values)

    # 4. Build PHDC
    builder = PHDCBuilder()
    builder.set_input_data(input_data)
    phdc = builder.build()

    return Response(content=phdc.to_xml_string(), media_type="application/xml")


# /schemas endpoint #
raw_list_schemas_response = read_json_from_assets("sample_list_schemas_response.json")
sample_list_schemas_response = {200: raw_list_schemas_response}


@app.get("/schemas", responses=sample_list_schemas_response)
async def list_schemas() -> ListSchemasResponse:
    """
    Get a list of all the parsing schemas currently available. Default schemas are ones
    that are packaged by default with this service. Custom schemas are any additional
    schema that users have chosen to upload to this service (this feature is not yet
    implemented)
    """
    default_schemas = os.listdir(Path(__file__).parent / "default_schemas")
    custom_schemas = os.listdir(Path(__file__).parent / "custom_schemas")
    custom_schemas = [schema for schema in custom_schemas if schema != ".keep"]
    schemas = {"default_schemas": default_schemas, "custom_schemas": custom_schemas}
    return schemas


# /schemas/{parsing_schema_name} endpoint #
raw_get_schema_response = read_json_from_assets("sample_get_schema_response.json")
sample_get_schema_response = {200: raw_get_schema_response}


@app.get(
    "/schemas/{parsing_schema_name}",
    status_code=200,
    responses=sample_get_schema_response,
)
async def get_schema(parsing_schema_name: str, response: Response) -> GetSchemaResponse:
    """
    Get the schema specified by 'parsing_schema_name'.
    """
    try:
        parsing_schema = load_parsing_schema(parsing_schema_name)
    except FileNotFoundError as error:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": error.__str__(), "parsing_schema": {}}
    return {"message": "Schema found!", "parsing_schema": parsing_schema}


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
    "/schemas/{parsing_schema_name}",
    status_code=200,
    response_model=PutSchemaResponse,
    responses=upload_schema_response_examples,
)
async def upload_schema(
    parsing_schema_name: str,
    input: Annotated[ParsingSchemaModel, Body(examples=upload_schema_request_examples)],
    response: Response,
) -> PutSchemaResponse:
    """
    Upload a new parsing schema to the service or update an existing schema.
    """

    file_path = Path(__file__).parent / "custom_schemas" / parsing_schema_name
    schema_exists = file_path.exists()
    if schema_exists and not input.overwrite:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": f"A schema for the name '{parsing_schema_name}' already exists. "
            "To proceed submit a new request with a different schema name or set the "
            "'overwrite' field to 'true'."
        }

    # Convert Pydantic models to dicts so they can be serialized to JSON.
    for field in input.parsing_schema:
        field_dict = input.parsing_schema[field].dict()
        if "secondary_schema" in field_dict and field_dict["secondary_schema"] is None:
            del field_dict["secondary_schema"]
        input.parsing_schema[field] = field_dict

    with open(file_path, "w") as file:
        json.dump(input.parsing_schema, file, indent=4)

    if schema_exists:
        return {"message": "Schema updated successfully!"}
    else:
        response.status_code = status.HTTP_201_CREATED
        return {"message": "Schema uploaded successfully!"}
