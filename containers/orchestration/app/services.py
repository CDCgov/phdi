import json
import os

import requests
from app.DAL.PostgresFhirDataModel import PostgresFhirDataModel
from app.DAL.SqlFhirRepository import SqlAlchemyFhirRepository
from app.utils import CustomJSONResponse
from fastapi import HTTPException
from fastapi import Response
from fastapi import WebSocket
from fastapi.encoders import jsonable_encoder
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from phdi.fhir.conversion.convert import _get_fhir_conversion_settings
from phdi.fhir.conversion.convert import standardize_hl7_datetimes


service_urls = {
    "validation": os.environ.get("VALIDATION_URL"),
    "ingestion": os.environ.get("INGESTION_URL"),
    "fhir_converter": os.environ.get("FHIR_CONVERTER_URL"),
    "message_parser": os.environ.get("MESSAGE_PARSER_URL"),
    "save_to_db": os.environ.get("DATABASE_URL"),
}


def validation_payload(**kwargs) -> dict:
    """
    The input payload to an orchestrated request of the DIBBs validation
    service. No additional configuration options are needed here beyond
    the supplied input.
    """
    input = kwargs["input"]
    return {
        "message_type": "ecr",
        "include_error_types": "errors",
        "message": input.get("message"),
        "rr_data": input.get("rr_data"),
    }


def validate_response(**kwargs) -> bool:
    """
    The body payload of a response from the DIBBs validation service. Reports
    whether a supplied message is valid.
    """
    response = kwargs["response"]
    body = response.json()
    if "message_valid" in body:
        return body.get("message_valid")

    return response.status_code == 200


def fhir_converter_payload(**kwargs) -> dict:
    """
    The input payload to an orchestrated request of the DIBBs FHIR converter
    service. When the user uploads data, we use the properties of the
    uploaded message to determine the appropriate conversion settings
    (such as the root template or HL7v2 basis segment). If these values
    cannot be determined directly from the message, the payload is set
    with default permissive EICR templates (needed to preserve
    compatibility with demo UI viewers.)
    """
    input = kwargs["input"]
    msg = str(input["message"])
    # Template will depend on input data formatting and typing, so try
    # to figure that out. If we can't, use our default EICR settings
    # to preserve backwards compatibility
    try:
        conversion_settings = _get_fhir_conversion_settings(msg)
        if conversion_settings["input_type"] == "hl7v2":
            msg = standardize_hl7_datetimes(msg)
    except KeyError:
        conversion_settings = {"input_type": "ecr", "root_template": "EICR"}
    return {
        "input_data": msg,
        "input_type": conversion_settings["input_type"],
        "root_template": conversion_settings["root_template"],
        "rr_data": input.get("rr_data"),
    }


def ingestion_payload(**kwargs) -> dict:
    """
    The input payload to an orchestrated request to the DIBBs ingestion
    service. The ingestion service comprises the DIBBs harmonization and
    geocoding offerings, so settings related to options for these
    functions are set in this payload.
    """
    response = kwargs["response"]
    step = kwargs["step"]
    config = kwargs["config"]
    r = response.json()
    endpoint = step["endpoint"] if "endpoint" in step else ""
    if "standardize_names" in endpoint:
        data = {"data": r["response"]["FhirResource"]}
    elif "geocode" in endpoint:
        data = {
            "bundle": r["bundle"],
            "geocode_method": config["configurations"]["ingestion"][
                "standardization_and_geocoding"
            ]["geocode_method"],
            "smarty_auth_id": os.environ.get("SMARTY_AUTH_ID"),
            "smarty_auth_token": os.environ.get("SMARTY_AUTH_TOKEN"),
            "license_type": os.environ.get("LICENSE_TYPE"),
        }
    else:
        data = {"data": r["bundle"]}
    return data


def message_parser_payload(**kwargs) -> dict:
    """
    The input payload of an orchestrated request to the DIBBs message parser
    service. The message parser could be used for internal tabular value
    extraction (`parse-message`) or conversion to PHDC (`fhir-to-phdc`), so
    the configuration settings of the user's chosen workflow determine which
    endpoint this payload is meant for.
    """
    response = kwargs["response"]
    config = kwargs["config"]
    r = response.json()

    # We determine which endpoint to hit by finding the message-parsing
    # service step and checking the desired call
    data = {"message": r["bundle"]}
    for step in config["steps"]:
        if step["service"] == "message_parser":
            if "fhir_to_phdc" in step["endpoint"]:
                data["phdc_report_type"] = config["configurations"]["message_parser"][
                    "phdc_report_type"
                ]
            else:
                data["message_format"] = config["configurations"]["message_parser"][
                    "message_format"
                ]
                data["parsing_schema_name"] = config["configurations"][
                    "message_parser"
                ]["parsing_schema_name"]
            break
    return data


def save_to_db(**kwargs) -> dict:
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
    bundle = kwargs["bundle"]
    b = bundle.json()
    if "bundle" in b:
        b = b["bundle"]
    if b.get("entry", {})[0].get("resource"):
        ecr_id = b["entry"][0]["resource"]["id"]
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
    r = response.json()
    if "bundle" in r:
        return response
    else:
        return bundle


async def call_apis(
    config,
    input,
    websocket: WebSocket = None,
) -> tuple:
    response = input
    responses = {}
    bundle = {}

    progress_dict = {"steps": config["steps"]}
    for step in config["steps"]:
        service = step["service"]
        endpoint = step["endpoint"]
        f = f"{service}_payload"
        if f in globals() and callable(globals()[f]) and service_urls[service]:
            function_to_call = globals()[f]
            payload = function_to_call(
                input=input, response=response, step=step, config=config, bundle=bundle
            )
            url = service_urls[service] + step["endpoint"]
            url = url.replace('"', "")
            print(f"Url: {url}")
            if service in globals() and callable(globals()[service]):
                response = globals()[service](url=url, payload=payload)
            else:
                response = post_request(url, payload)
            bundle = save_bundle(response, bundle)
            print(f"Status Code: {response.status_code}")

            if websocket:
                endpoint_name = f"{response.url.split('/')[-1]}"
                status = "success" if validate_response(response=response) else "error"

                # Write service responses into websocket message
                progress_dict[endpoint_name] = {
                    "status": status,
                    "status_code": response.status_code,
                    "response": response.json(),
                }

                await websocket.send_text(json.dumps(progress_dict))

            if validate_response(response=response) is False:
                break

            responses[endpoint] = response
        else:
            raise HTTPException(
                status_code=422,
                detail="The Building Block you are attempting to call does not exist:"
                + f" {service}",
            )
    return response, responses
