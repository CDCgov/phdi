import json
import os
from json.decoder import JSONDecodeError

import requests
from app.DAL.PostgresFhirDataModel import PostgresFhirDataModel
from app.DAL.SqlFhirRepository import SqlAlchemyFhirRepository
from app.handlers import build_fhir_converter_request
from app.handlers import build_geocoding_request
from app.handlers import build_ingestion_dob_request
from app.handlers import build_ingestion_name_request
from app.handlers import build_ingestion_phone_request
from app.handlers import build_message_parser_message_request
from app.handlers import build_message_parser_phdc_request
from app.handlers import build_validation_request
from app.handlers import ServiceHandlerResponse
from app.handlers import unpack_fhir_converter_response
from app.handlers import unpack_fhir_to_phdc_response
from app.handlers import unpack_ingestion_standardization
from app.handlers import unpack_parsed_message_response
from app.handlers import unpack_validation_response
from app.models import OrchestrationRequest
from app.utils import CustomJSONResponse
from app.utils import format_service_url
from fastapi import HTTPException
from fastapi import Response
from fastapi import WebSocket
from fastapi.encoders import jsonable_encoder
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


# Locations of the various services the service will delegate
SERVICE_URLS = {
    "validation": os.environ.get("VALIDATION_URL"),
    "ingestion": os.environ.get("INGESTION_URL"),
    "fhir_converter": os.environ.get("FHIR_CONVERTER_URL"),
    "message_parser": os.environ.get("MESSAGE_PARSER_URL"),
    "save_to_db": os.environ.get("DATABASE_URL"),
}

# Mappings of endpoint names to the service input and output building
# functions--lets the workflow config drive the API loop with no need
# to change function signatures
ENDPOINT_TO_REQUEST = {
    "validate": build_validation_request,
    "convert-to-fhir": build_fhir_converter_request,
    "geocode_bundle": build_geocoding_request,
    "standardize_names": build_ingestion_name_request,
    "standardize_dob": build_ingestion_dob_request,
    "standardize_phones": build_ingestion_phone_request,
    "parse_message": build_message_parser_message_request,
    "fhir_to_phdc": build_message_parser_phdc_request,
}
ENDPOINT_TO_RESPONSE = {
    "validate": unpack_validation_response,
    "convert-to-fhir": unpack_fhir_converter_response,
    "geocode_bundle": unpack_ingestion_standardization,
    "standardize_names": unpack_ingestion_standardization,
    "standardize_dob": unpack_ingestion_standardization,
    "standardize_phones": unpack_ingestion_standardization,
    "parse_message": unpack_parsed_message_response,
    "fhir_to_phdc": unpack_fhir_to_phdc_response,
}


def save_to_db(**kwargs) -> dict:
    """
    Currently, a temporary function taking the place of a save to DB
    endpoint. Once this endpoint exists in the eCR viewer, we can
    write full-fledged request and response handlers for this service.
    """
    ecr_id = kwargs["payload"]["ecr_id"]
    payload_data = kwargs["payload"]["data"]
    url = kwargs["url"]
    engine = create_engine(url)
    pg_data = PostgresFhirDataModel(ecr_id=str(ecr_id), data=payload_data)
    try:
        with Session(engine, expire_on_commit=False) as session:
            repo = SqlAlchemyFhirRepository(session)
            repo.persist(pg_data)
        return CustomJSONResponse(content=jsonable_encoder(payload_data), url=url)
    except SQLAlchemyError as e:
        return Response(content=e, status_code=500)


def save_to_db_payload(**kwargs) -> dict:
    """
    Currently, a temporary function taking the place of a save to DB
    payload. Once this endpoint exists in the eCR viewer, we can
    write full-fledged request and response handlers for this service.
    """

    if "bundle" not in kwargs:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "Unprocessable Entity",
                "details": "Bundle not provided to save_to_db payload",
            },
        )
    bundle = kwargs["bundle"]
    b = bundle.json()
    if "bundle" in b:
        b = b["bundle"]
    entry = b.get("entry") if isinstance(b, dict) and b.get("entry") else False
    first_entry = entry[0] if entry else False
    resource = first_entry.get("resource") if first_entry else False

    if entry and first_entry and resource:
        ecr_id = resource.get("id")
    else:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "Unprocessable Entity",
                "details": "eICR ID not found, cannot save to database.",
            },
        )
    return {"ecr_id": ecr_id, "data": b}


def post_request(url, payload):
    return requests.post(url, json=payload)


def save_bundle(response, bundle):
    try:
        r = response.json()
        if "bundle" in r:
            return response
        else:
            return bundle
    except JSONDecodeError as e:
        print("Failed to decode JSON:", e)
        return bundle


async def _send_websocket_dump(
    endpoint_name: str,
    base_response: Response,
    service_response: ServiceHandlerResponse,
    progress_dict: dict,
    websocket: WebSocket,
) -> dict:
    """
    Helper method that sends service response information from a DIBBs
    API call to a particular web socket.
    :param endpoint_name: Name of the endpoint to inform the websocket of.
    :param base_response: The unaltered response the service sent back.
    :param service_response: The unpacked handler response with logic
      applied determining whether the calling function should continue.
    :param progress_dict: The dictionary tracking progres to notify the
      websocket of.
    :param websocket: The websocket to stream the data to.
    :return: The updated progress dictionary.
    """
    status = (
        "success"
        if (service_response.status_code == 200 and service_response.should_continue)
        else "error"
    )

    # Write service responses into websocket message
    progress_dict[endpoint_name] = {
        "status": status,
        "status_code": base_response.status_code,
        "response": base_response.json(),
    }

    await websocket.send_text(json.dumps(progress_dict))
    return progress_dict


async def call_apis(
    config: dict, input: OrchestrationRequest, websocket: WebSocket = None
) -> tuple:
    """
    Asynchronous function that loops over each step in a provided workflow
    config and performs each service step. The function builds a request
    packet for each step, posts to the appropriate API, then unpacks the
    service response. If the response is valid and has data, it is passed
    to the next service as input. If the response was unsuccessful, the
    function communicates errors to the caller.
    :param config: The config-driven workflow extracted from a JSON file.
    :param input: The original request to the orchestration service.
    :param websocket: Optionally, a socket to which to stream input
      bytes on the service's progress and results.
    :return: A tuple holding the concluding status code of the orchestration
      service, as well as each step's response along the way.
    """
    workflow = config.get("workflow", [])
    current_message = input.get("message")
    response = current_message
    responses = {}
    bundle = {}
    # For websocket json dumps
    progress_dict = {}
    for step in workflow:
        service = step["service"]
        endpoint = step["endpoint"]
        endpoint_name = endpoint.split("/")[-1]
        params = step.get("params", None)

        service_url = format_service_url(SERVICE_URLS[service], endpoint)

        # TODO: Once the save to DB functionality is registered as an actual
        # service endpoint on the eCR viewer side, we can write real handlers
        # for it and take out the if/else logic
        if service != "save_to_db":
            request_func = ENDPOINT_TO_REQUEST[endpoint_name]
            response_func = ENDPOINT_TO_RESPONSE[endpoint_name]
            service_request = request_func(current_message, input, params)
            response = post_request(service_url, service_request)
            bundle = save_bundle(response=response, bundle=bundle)

            service_response = response_func(response)

            if websocket:
                progress_dict = await _send_websocket_dump(
                    endpoint_name,
                    response,
                    service_response,
                    progress_dict,
                    websocket,
                )

            if service_response.status_code != 200:
                raise HTTPException(
                    status_code=service_response.status_code,
                    detail=f"Service {service} failed with error {service_response.msg_content}",  # noqa
                )

            if not service_response.should_continue:
                raise HTTPException(
                    status_code=400,
                    detail=f"Service {service} completed, but orchestration cannot continue: "  # noqa
                    + f"{service_response.msg_content}",
                )

            # Validation reports only whether we should continue, with
            # no updated data, so don't send error results to next
            # service
            if service != "validation":
                current_message = service_response.msg_content
            responses[service] = response
        else:
            db_request = save_to_db_payload(response=response, bundle=bundle)
            response = save_to_db(url=service_url, payload=db_request)
            if websocket:
                progress_dict = await _send_websocket_dump(
                    endpoint_name,
                    response,
                    service_response,
                    progress_dict,
                    websocket,
                )

            responses[service] = response

    return (response, responses)
