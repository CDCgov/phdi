from phdi.containers.base_service import BaseService
from fastapi import Response, status, Body, UploadFile, Form
from pydantic import BaseModel, Field
from typing import Literal, Optional, Annotated, Dict
from pathlib import Path
from zipfile import ZipFile
import io
import os
from app.utils import load_processing_config, read_json_from_assets
from app.config import get_settings
import requests
import json

# Read settings immediately to fail fast in case there are invalid values.
get_settings()

# Instantiate FastAPI via PHDI's BaseService class
app = BaseService(
    service_name="PHDI Orchestration",
    description_path=Path(__file__).parent.parent / "description.md",
).start()

# /process endpoint #
process_message_request_examples = read_json_from_assets(
    "sample_process_message_requests.json"
)
raw_process_message_response_examples = read_json_from_assets(
    "sample_process_message_responses.json"
)
process_message_response_examples = {200: raw_process_message_response_examples}

processing_config = load_processing_config("sample-orchestration-config.json")

message_parser_url = os.environ.get("MESSAGE_PARSER_URL")
validation_url = os.environ.get("VALIDATION_URL")
fhir_converter_url = os.environ.get("FHIR_CONVERTER_URL")
ingestion_url = os.environ.get("INGESTION_URL")
stan_name_url = os.environ.get("STANDARDIZE_NAME_URL")
geocode_url = os.environ.get("GEOCODE_URL")


# Request and response models
class ProcessMessageRequest(BaseModel):
    """
    The config for requests to the /extract endpoint.
    """

    message_type: Literal["ecr", "elr", "vxu", "fhir"] = Field(
        description="The type of message to be validated."
    )
    include_error_types: str = Field(
        description=(
            "A comma separated list of the types of errors that should be"
            + " included in the return response."
            + " Valid types are fatal, errors, warnings, information"
        )
    )
    upload_file: UploadFile = Field(description="The ZIP file with ECR")


class ProcessMessageResponse(BaseModel):
    """
    The config for responses from the /extract endpoint.
    """

    message: str = Field(
        description="A message describing the result of a request to "
        "the /process endpoint."
    )
    processed_values: dict = Field(
        description="A set of key:value pairs containing the values extracted from the "
        "message."
    )


def call_validation(input, response, step) -> dict:
    data = {
        "message_type": "ecr",
        "include_error_types": "errors",
        "message": str(input["message"]),
    }
    validation_response = requests.post(validation_url + step["endpoint"], json=data)
    return validation_response


def call_fhir_converter(input, response, step) -> dict:
    data = {
        "input_data": str(input["message"]),
        "input_type": "ecr",
        "root_template": "EICR",
    }
    fhir_conversion_response = requests.post(
        fhir_converter_url + step["endpoint"], json=data
    )
    return fhir_conversion_response


def call_ingestion(input, response, step) -> dict:
    r = response.json()

    if "standardize_names" in step["endpoint"]:
        data = {"data": r["response"]["FhirResource"]}
    elif "geocode" in step["endpoint"]:
        data = {
            "bundle": r["bundle"],
            "geocode_method": processing_config["configurations"][
                "standardization_and_geocoding"
            ]["geocode_method"],
            "smarty_auth_id": os.environ.get("SMARTY_AUTH_ID"),
            "smarty_auth_token": os.environ.get("SMARTY_AUTH_TOKEN"),
            "license_type": os.environ.get("LICENSE_TYPE"),
        }
    else:
        data = {"data": r["bundle"]}

    ingestion_response = requests.post(ingestion_url + step["endpoint"], json=data)
    return ingestion_response


def call_message_parser(input, response, step) -> dict:
    r = response.json()
    data = {
        "message_format": processing_config["configurations"]["message_parser"][
            "message_format"
        ],
        "parsing_schema_name": processing_config["configurations"]["message_parser"][
            "parsing_schema_name"
        ],
        "message": r["bundle"],
    }

    message_parser_response = requests.post(
        message_parser_url + step["endpoint"], json=data
    )
    return message_parser_response


@app.post("/process", status_code=200, responses=process_message_response_examples)
async def process_message_endpoint(
    message_type: Annotated[str, Form()],
    include_error_types: Annotated[str, Form()],
    upload_file: UploadFile
) -> ProcessMessageResponse:
    """
    Process message through a series of microservices
    """
    # Unzip file
    # with ZipFile(io.BytesIO(upload_file.file.read()), 'r') as zip:
    #   pass
    my_zipfile = ZipFile(upload_file.file)
    print(my_zipfile.namelist())
    f = my_zipfile.open("f1ef2b9d-9af3-4228-bb28-d3a5a1c5cd9d/CDA_eICR.xml")
    content = f.read()
    print(content)
    return {
            "message": "Request failed with status code",
            "processed_values": "",
        }

    # # Change below to grab from uploaded configs once we've got them
    # processing_config = load_processing_config("sample-orchestration-config.json")
    # input = dict(input)
    # response = input
    # responses = {}

    # for step in processing_config["steps"]:
    #     service = step["service"]
    #     endpoint = step["endpoint"]
    #     f = f"call_{service}"
    #     if f in globals() and callable(globals()[f]):
    #         function_to_call = globals()[f]
    #         response = function_to_call(input=input, response=response, step=step)
    #         responses[endpoint] = response

    # if response.status_code == 200:
    #     # Parse and work with the API response data (JSON, XML, etc.)
    #     api_data = response.json()  # Assuming the response is in JSON format
    #     return {
    #         "message": "Processing succeeded!",
    #         "processed_values": api_data,
    #     }
    # else:
    #     return {
    #         "message": f"Request failed with status code {response.status_code}",
    #         "processed_values": "",
    #     }


# /configs endpoint #
raw_list_configs_response = read_json_from_assets("sample_list_configs_response.json")
sample_list_configs_response = {200: raw_list_configs_response}


class ListConfigsResponse(BaseModel):
    """
    The config for responses from the /configs endpoint.
    """

    default_configs: list = Field(
        description="The configs that ship with with this service by default."
    )
    custom_configs: list = Field(
        description="Additional configs that users have uploaded to this service beyond"
        " the ones come by default."
    )


@app.get("/configs", responses=sample_list_configs_response)
async def list_configs() -> ListConfigsResponse:
    """
    Get a list of all the process configs currently available. Default configs are ones
    that are packaged by default with this service. Custom configs are any additional
    config that users have chosen to upload to this service (this feature is not yet
    implemented)
    """
    default_configs = os.listdir(Path(__file__).parent / "default_configs")
    custom_configs = os.listdir(Path(__file__).parent / "custom_configs")
    custom_configs = [config for config in custom_configs if config != ".keep"]
    configs = {"default_configs": default_configs, "custom_configs": custom_configs}
    return configs


class GetConfigResponse(BaseModel):
    """
    The config for responses from the /configs endpoint when a specific config is
    queried.
    """

    message: str = Field(
        description="A message describing the result of a request to "
        "the /process endpoint."
    )
    processing_config: dict = Field(
        description="A configuration for the orchestration app"
    )


# /configs/{processing_config_name} endpoint #
raw_get_config_response = read_json_from_assets("sample_get_config_response.json")
sample_get_config_response = {200: raw_get_config_response}


@app.get(
    "/configs/{processing_config_name}",
    status_code=200,
    responses=sample_get_config_response,
)
async def get_config(
    processing_config_name: str, response: Response
) -> GetConfigResponse:
    """
    Get the config specified by 'processing_config_name'.
    """
    try:
        processing_config = load_processing_config(processing_config_name)
    except FileNotFoundError as error:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": error.__str__(), "processing_config": {}}
    return {"message": "Config found!", "processing_config": processing_config}


PROCESSING_CONFIG_DATA_TYPES = Literal[
    "string", "integer", "float", "boolean", "date", "timestamp"
]


class ProcessingConfigSecondaryFieldModel(BaseModel):
    fhir_path: str
    data_type: PROCESSING_CONFIG_DATA_TYPES
    nullable: bool


class ProcessingConfigFieldModel(BaseModel):
    fhir_path: str
    data_type: PROCESSING_CONFIG_DATA_TYPES
    nullable: bool
    secondary_config: Dict[str, ProcessingConfigSecondaryFieldModel]


class ProcessingConfigModel(BaseModel):
    processing_config: Dict[str, ProcessingConfigFieldModel] = Field(
        description="A JSON formatted processing config to upload."
    )
    overwrite: Optional[bool] = Field(
        description="When `true` if a config already exists for the provided name it "
        "will be replaced. When `false` no action will be taken and the response will "
        "indicate that a config for the given name already exists. To proceed submit a "
        "new request with a different config name or set this field to `true`.",
        default=False,
    )


class PutConfigResponse(BaseModel):
    """
    The config for responses from the /configs endpoint when a config is uploaded.
    """

    message: str = Field(
        'A message describing the result of a request to "/configs/"upload a processing'
        + "config."
    )


upload_config_request_examples = read_json_from_assets(
    "sample_upload_config_requests.json"
)

upload_config_response_examples = {
    200: "sample_upload_config_response.json",
    201: "sample_update_config_response.json",
    400: "sample_upload_config_failure_response.json",
}
for status_code, file_name in upload_config_response_examples.items():
    upload_config_response_examples[status_code] = read_json_from_assets(file_name)
    upload_config_response_examples[status_code]["model"] = PutConfigResponse


@app.put(
    "/configs/{processing_config_name}",
    status_code=200,
    response_model=PutConfigResponse,
    responses=upload_config_response_examples,
)
async def upload_config(
    processing_config_name: str,
    input: Annotated[
        ProcessingConfigModel, Body(examples=upload_config_request_examples)
    ],
    response: Response,
) -> PutConfigResponse:
    """
    Upload a new processing config to the service or update an existing config.
    """

    file_path = Path(__file__).parent / "custom_configs" / processing_config_name
    config_exists = file_path.exists()
    if config_exists and not input.overwrite:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": f"A config for the name '{processing_config_name}' already "
            "exists. To proceed submit a new request with a different config name or "
            "set the 'overwrite' field to 'true'."
        }

    # Convert Pydantic models to dicts so they can be serialized to JSON.
    for field in input.processing_config:
        input.processing_config[field] = input.processing_config[field].dict()

    with open(file_path, "w") as file:
        json.dump(input.processing_config, file, indent=4)

    if config_exists:
        return {"message": "Config updated successfully!"}
    else:
        response.status_code = status.HTTP_201_CREATED
        return {"message": "Config uploaded successfully!"}
