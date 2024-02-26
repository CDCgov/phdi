import json
import logging
import os
from pathlib import Path
from typing import Annotated

from app.config import get_settings
from app.constants import process_message_response_examples
from app.constants import sample_get_config_response
from app.constants import sample_list_configs_response
from app.constants import upload_config_response_examples
from app.models import GetConfigResponse
from app.models import ListConfigsResponse
from app.models import OrchestrationRequest
from app.models import OrchestrationResponse
from app.models import ProcessingConfigModel
from app.models import PutConfigResponse
from app.services import call_apis
from app.services import validate_response
from app.utils import load_config_assets
from app.utils import load_json_from_binary
from app.utils import load_processing_config
from app.utils import unzip_http
from app.utils import unzip_ws
from fastapi import Body
from fastapi import File
from fastapi import Form
from fastapi import Response
from fastapi import status
from fastapi import UploadFile
from fastapi import WebSocket
from fastapi import WebSocketDisconnect

from phdi.containers.base_service import BaseService

logger = logging.getLogger(__name__)

# Read settings immediately to fail fast in case there are invalid values.
get_settings()

# Instantiate FastAPI via PHDI's BaseService class
app = BaseService(
    service_name="PHDI Orchestration",
    service_path="/orchestration",
    description_path=Path(__file__).parent.parent / "description.md",
).start()


upload_config_response = load_config_assets(
    upload_config_response_examples, PutConfigResponse
)


class WS_File:
    """
    A class to represent a file object for WebSocket communication.

    This class is designed to handle file data that is transmitted over
    a WebSocket connection.
    """

    # Constructor method (init method)
    def __init__(self, file):
        # Instance attributes
        self.file = file


@app.websocket("/process-ws")
async def process_message_endpoint_ws(
    websocket: WebSocket,
) -> OrchestrationResponse:
    """
    Creates a websocket connection with the client and accepts a zipped XML file.
    The file is processed by the building blocks according to the currently
    loaded configuration and emits websocket updates to the client as each
    processing step completes.

    :param websocket:An instance of the WebSocket connection. It is used to communicate
      with the client, sending and receiving data in real-time.
    """

    await websocket.accept()
    try:
        while True:
            file_bytes = await websocket.receive_bytes()
            unzipped_data = unzip_ws(file_bytes)

            # Hardcoded message_type for MVP
            initial_input = {
                "message_type": "ecr",
                "include_error_types": "errors",
                "message": unzipped_data.get("ecr"),
                "rr_data": unzipped_data.get("rr"),
            }
            processing_config = load_processing_config(
                "sample-orchestration-config-new.json"
            )
            response, responses = await call_apis(
                config=processing_config, input=initial_input, websocket=websocket
            )
            if validate_response(response=response):
                # Parse and work with the API response data (JSON, XML, etc.)
                api_data = response.json()  # Assuming the response is in JSON format
                message = {
                    "message": "Processing succeeded!",
                    "processed_values": api_data,
                }
                await websocket.send_text(json.dumps(message))
    except WebSocketDisconnect:
        logger.error("The websocket disconnected")
    except Exception as e:
        logger.error("An error occurred:", e)
        if websocket:
            await websocket.send_text(
                json.dumps(
                    {
                        "message": "Something went wrong",
                        "responses": None,
                        "processed_values": "",
                    }
                )
            )
    finally:
        await websocket.close()


# TODO: This method needs request validation on message_type and include_error_types
# Should make them into Field values and validate with Pydantic
@app.post("/process", status_code=200, responses=process_message_response_examples)
async def process_endpoint(
    message_type: str = Form(None),
    data_type: str = Form(None),
    config_file_name: str = Form(None),
    include_error_types: str = Form(None),
    upload_file: UploadFile = File(None),
) -> OrchestrationResponse:
    """
    Wrapper function for unpacking an uploaded file, determining appropriate
    parameter and application settings, and applying a config-driven workflow
    to the data in that file. This is one of two endpoints that can actually
    invoke and apply a config workflow to data and is meant to be used to
    process files.

    :param message_type: The type of stream of the uploaded file's underlying
      data (e.g. ecr, elr, etc.). If the data is in FHIR format, set to FHIR.
    :param data_type: The type of data held in the uploaded file. Eligible
      values include `ecr`, `zip`, `fhir`, and `hl7`.
    :param config_file_name: The name of the configuration file to load on
      the service's back-end, specifying the workflow to apply.
    :param include_error_types: Whether to include error messaging if the
      workflow is unsuccessful, as well as what kinds of errors.
    :param upload_file: A file containing clinical health care information.
    :return: A response holding whether the workflow application was
      successful as well as the results of the workflow.
    """

    rr_content = None
    if upload_file.content_type == "application/zip":
        unzipped_file = unzip_http(upload_file)
        message = unzipped_file.get("ecr")
        rr_content = unzipped_file.get("rr")
    elif upload_file.content_type == "application/json":
        message = load_json_from_binary(upload_file)
    else:
        message = upload_file.read()

    building_block_response = await apply_workflow_to_message(
        message_type,
        data_type,
        config_file_name,
        include_error_types,
        message,
        rr_content,
    )

    return building_block_response


@app.post(
    "/process-message", status_code=200, responses=process_message_response_examples
)
async def process_message_endpoint(
    request: OrchestrationRequest,
) -> OrchestrationResponse:
    """
    Wrapper function for unpacking a message processing input and using those
    settings to apply a config-driven workflow to a raw string of data.
    This endpoint is the second of two workflow-driven endpoints and is meant
    to be used with raw string data (meaning if the data is JSON, it must be
    string serialized with `json.dumps`).

    :param request: A response holding whether the workflow application was
      successful as well as the results of the workflow.
    """
    process_request = dict(request)
    building_block_response = await apply_workflow_to_message(
        process_request.get("message_type"),
        process_request.get("data_type"),
        process_request.get("config_file_name"),
        process_request.get("include_error_types"),
        process_request.get("message"),
        process_request.get("rr_data"),
    )

    return building_block_response


async def apply_workflow_to_message(
    message_type: str,
    data_type: str,
    config_file_name: str,
    include_error_types: str,
    message: str,
    rr_content: str,
) -> Response:
    """
    Main orchestration function that applies a config-defined workflow to an
    uploaded piece of data. The workflow applied is determined by loading the
    configuration file of the provided name, and each step of this workflow
    is applied by an appropriate API call.

    :param message_type: The type of data being supplied for orchestration. May
      be either 'ecr', 'elr', 'vxu', or 'fhir'.
    :param data_type: The type of data of the passed-in message.
    :param config_file_name: The name of the workflow configuration file to
      load and apply stepwise to the data. File must be located in the custom
      or default configs directory on the service's disk space.
    :param include_error_types: Whether to include error typing in the API
      responses.
    :param message: The content of the supplied string of data.
    :param rr_content: The reportability response associated with the eCR.
    :return: Response of whether the workflow succeeded and what its outputs
      were.
    """
    # Load the config file and fail fast if we can't find it
    try:
        processing_config = load_processing_config(config_file_name)
    except FileNotFoundError as error:
        response = Response(
            content=json.dumps(
                {
                    "message": error.__str__(),
                    "processed_values": {},
                }
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
        return response

    # Compile the input to the other service endpoints and call them
    api_input = {
        "message_type": message_type,
        "data_type": data_type,
        "include_error_types": include_error_types,
        "message": message,
        "rr_data": rr_content,
    }
    response, responses = await call_apis(config=processing_config, input=api_input)

    if response.status_code == 200:
        content_type = response.headers.get("content-type", "")
        if "application/xml" in content_type or "text/xml" in content_type:
            # Handle XML data as a string
            api_data = response.content
            return Response(content=api_data, media_type="application/xml")
        elif "application/json" in content_type:
            # Return JSON data
            api_data = response.json()
            return Response(
                content=json.dumps(
                    {"message": "Processing succeeded!", "processed_values": api_data}
                ),
                media_type="application/json",
            )
        else:
            api_data = response.text
            return Response(content=api_data)
    else:
        # Return error as JSON
        return Response(
            content=json.dumps(
                {
                    "message": f"Request fail with status code {response.status_code}",
                    "responses": responses,
                    "processed_values": "",
                }
            ),
            media_type="application/json",
            status_code=response.status_code,
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

    :param processing_config_name: The name of the processing configuration to retrieve.
    :param response: The response object used to modify the response status and body.
    """
    try:
        processing_config = load_processing_config(processing_config_name)
    except FileNotFoundError as error:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": error.__str__(), "processing_config": {}}
    return {"message": "Config found!", "processing_config": processing_config}


@app.put(
    "/configs/{processing_config_name}",
    status_code=200,
    response_model=PutConfigResponse,
    responses=upload_config_response,
)
async def upload_config(
    processing_config_name: str,
    input: Annotated[ProcessingConfigModel, Body(examples=upload_config_response)],
    response: Response,
) -> PutConfigResponse:
    """
    Upload a new processing config to the service or update an existing config.

    :param processing_config_name: The name of the processing configuration to be
      uploaded or updated.
    :param input: A Pydantic model representing the processing configuration data.
    :param response: The response object used to modify the response status and body.
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
