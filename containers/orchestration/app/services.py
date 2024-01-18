import json
import os
import uuid

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


service_urls = {
    "validation": os.environ.get("VALIDATION_URL"),
    "ingestion": os.environ.get("INGESTION_URL"),
    "fhir_converter": os.environ.get("FHIR_CONVERTER_URL"),
    "message_parser": os.environ.get("MESSAGE_PARSER_URL"),
    "save_to_db": os.environ.get("DATABASE_URL"),
}


def validation_payload(**kwargs) -> dict:
    input = kwargs["input"]
    return {
        "message_type": "ecr",
        "include_error_types": "errors",
        "message": input.get("message"),
        "rr_data": input.get("rr_data"),
    }


def validate_response(**kwargs) -> bool:
    response = kwargs["response"]
    body = response.json()
    if "message_valid" in body:
        return body.get("message_valid")

    return response.status_code == 200


def fhir_converter_payload(**kwargs) -> dict:
    input = kwargs["input"]
    return {
        "input_data": str(input["message"]),
        "input_type": "ecr",
        "root_template": "EICR",
        "rr_data": input.get("rr_data"),
    }


def ingestion_payload(**kwargs) -> dict:
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
    response = kwargs["response"]
    config = kwargs["config"]
    r = response.json()
    data = {
        "message_format": config["configurations"]["message_parser"]["message_format"],
        "parsing_schema_name": config["configurations"]["message_parser"][
            "parsing_schema_name"
        ],
        "message": r["bundle"],
    }
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
    response = kwargs["response"]
    r = response.json()
    if r.get("parsed_values", {}).get("eicr_id"):
        ecr_id = r["parsed_values"]["eicr_id"]
    else:
        ecr_id = uuid.uuid4()
    return {"ecr_id": ecr_id, "data": r}


def post_request(url, payload):
    return requests.post(url, json=payload)


async def call_apis(
    config,
    input,
    websocket: WebSocket = None,
) -> tuple:
    response = input
    responses = {}

    progress_dict = {"steps": config["steps"]}
    for step in config["steps"]:
        service = step["service"]
        endpoint = step["endpoint"]
        f = f"{service}_payload"
        if f in globals() and callable(globals()[f]) and service_urls[service]:
            function_to_call = globals()[f]
            payload = function_to_call(
                input=input, response=response, step=step, config=config
            )
            url = service_urls[service] + step["endpoint"]
            url = url.replace('"', "")
            print(f"Url: {url}")
            if service in globals() and callable(globals()[service]):
                response = globals()[service](url=url, payload=payload)
            else:
                response = post_request(url, payload)
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
