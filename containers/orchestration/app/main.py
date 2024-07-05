import json
import logging
import os
from pathlib import Path
from typing import Annotated

from dibbs.base_service import BaseService
from fastapi import Body
from fastapi import File
from fastapi import Form
from fastapi import Response
from fastapi import status
from fastapi import UploadFile
from fastapi import WebSocket
from fastapi import WebSocketDisconnect
from opentelemetry import metrics
from opentelemetry import trace
from opentelemetry.trace.status import StatusCode

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
from app.utils import _combine_response_bundles
from app.utils import _socket_response_is_valid
from app.utils import load_config_assets
from app.utils import load_json_from_binary
from app.utils import load_processing_config
from app.utils import unzip_http
from app.utils import unzip_ws

# Integrate main app tracer with automatic instrumentation context
tracer = trace.get_tracer("orchestration_main_tracer")

logger = logging.getLogger(__name__)
meter = metrics.get_meter("orchestration_main_meter")

# Read settings immediately to fail fast in case there are invalid values.
get_settings()

# Configure metrics trackers
process_message_counter = meter.create_counter(
    "process_message_counter",
    description="The number of served requests returning each possible"
    " status code for the process_message endpoint.",
)
process_counter = meter.create_counter(
    "process_counter",
    description="The number of served requests returning each possible"
    " status code for the process endpoint.",
)

# Instantiate FastAPI via PHDI's BaseService class
app = BaseService(
    service_name="PHDI Orchestration",
    service_path="/orchestration",
    description_path=Path(__file__).parent.parent / "description.md",
    openapi_url="/orchestration/openapi.json",
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
                "message": unzipped_data.get("ecr"),
                "rr_data": unzipped_data.get("rr"),
            }
            processing_config = load_processing_config("test-no-save.json")
            response, responses = await call_apis(
                config=processing_config, input=initial_input, websocket=websocket
            )
            if _socket_response_is_valid(response=response):
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


# TODO: This method needs request validation on message_type
# Should make them into Field values and validate with Pydantic
@app.post("/process-zip", status_code=200, responses=process_message_response_examples)
async def process_zip_endpoint(
    message_type: str = Form(None),
    data_type: str = Form(None),
    config_file_name: str = Form(None),
    upload_file: UploadFile = File(None),
) -> OrchestrationResponse:
    """
    Wrapper function for unpacking an uploaded zip file, determining appropriate
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
        message,
        rr_content,
    )

    # Vacuous addition--if we got here without breaking, it's a 200,
    # or at least, can be treated as such for MVP metrics purposes
    process_counter.add(1, {"status_code": 200})

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

    # Store params as K-V pairs at span creation, and log workflow event
    # This is a `SERVER` span since it receives an inbound remote request
    with tracer.start_as_current_span(
        "process-message",
        kind=trace.SpanKind(1),
        attributes={
            "message_type": process_request.get("message_type"),
            "data_type": process_request.get("data_type"),
            "config_file_chosen": process_request.get("config_file_name"),
        },
    ) as pm_span:
        pm_span.add_event("sending data to apply workflow")

        building_block_response = await apply_workflow_to_message(
            process_request.get("message_type"),
            process_request.get("data_type"),
            process_request.get("config_file_name"),
            process_request.get("message"),
            process_request.get("rr_data"),
        )

        workflow_status = building_block_response.status_code
        pm_span.add_event(
            "building blocks responded",
            attributes={"workflow_status_code": workflow_status},
        )

        # Only override `UNSET` if return is fully successful
        # OpenTelemetry's `OK` value should be dev-finalized only
        if workflow_status == 200:
            pm_span.set_status(StatusCode(1))

        process_message_counter.add(1, {"status_code": workflow_status})

        return building_block_response


async def apply_workflow_to_message(
    message_type: str,
    data_type: str,
    config_file_name: str,
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
    :param message: The content of the supplied string of data.
    :param rr_content: The reportability response associated with the eCR.
    :return: Response of whether the workflow succeeded and what its outputs
      were.
    """

    with tracer.start_as_current_span(
        "apply-workflow-to-message",
        kind=trace.SpanKind(0),
        attributes={
            "message_type": message_type,
            "data_type": data_type,
            "config_file_chosen": config_file_name,
        },
    ) as wf_span:
        wf_span.add_event("attempting to load workflow config")

        # Load the config file and fail fast if we can't find it
        try:
            processing_config = load_processing_config(config_file_name)
            wf_span.add_event("config loaded successfully")
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
            wf_span.record_exception(FileNotFoundError)
            wf_span.set_status(
                StatusCode(2), "Could not load config: " + error.__str__()
            )
            return response

        # Compile the input to the other service endpoints and call them
        api_input = {
            "message_type": message_type,
            "data_type": data_type,
            "message": message,
            "rr_data": rr_content,
        }
        wf_span.add_event("sending params to `call_apis`")
        response, responses = await call_apis(config=processing_config, input=api_input)
        wf_span.add_event(
            "`call_apis` responded with computed result",
            attributes={"return_code": response.status_code},
        )

        # if not 200, return status code and any error messaging
        if response.status_code != 200:
            wf_span.add_event(
                "`call_apis` response not 200",
                attributes={"status_code": response.status_code},
            )
            return Response(
                content=json.dumps(
                    {
                        "message": "Request failed with status code "
                        + f"{response.status_code}",
                        "responses": _filter_failed_responses(responses),
                        "processed_values": "",
                    }
                ),
                media_type="application/json",
                status_code=response.status_code,
            )

        # determine how to process/return 200 data for json and xml
        content_type = response.headers.get("content-type", "")
        wf_span.add_event(
            "parsing content type", attributes={"content_type": content_type}
        )
        match content_type:
            case "application/xml" | "text/xml":
                workflow_content = response.content
            case "application/json":
                workflow_content = json.dumps(
                    {
                        "message": "Processing succeeded!",
                        "processed_values": _combine_response_bundles(
                            response, responses, processing_config
                        ),
                    }
                )
            case _:
                workflow_content = response.text

        wf_span.set_status(StatusCode(1))
        return Response(content=workflow_content, media_type=content_type)


def _filter_failed_responses(responses):
    failed_responses = {}
    for key, item in responses.items():
        if item.status_code != 200:
            failed_responses[key] = item.json()

    return failed_responses


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
        return {"message": error.__str__(), "workflow": {}}
    return {"message": "Config found!", "workflow": processing_config}


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
    for i in range(len(input.workflow["workflow"])):
        input.workflow["workflow"][i] = input.workflow["workflow"][i].dict()

    with open(file_path, "w") as file:
        json.dump(input.workflow, file, indent=4)

    if config_exists:
        return {"message": "Config updated successfully!"}
    else:
        response.status_code = status.HTTP_201_CREATED
        return {"message": "Config uploaded successfully!"}


# This block is only executed if the script is run directly, for local development, debugging.
if "__main__" == __name__:
    import uvicorn

    uvicorn.run(
        app="app.main:app",
        host="0.0.0.0",
        port=8080,
        env_file="local-dev.env",
        reload=True,
    )
