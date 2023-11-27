import os
import requests
import json
from fastapi import HTTPException, WebSocket


service_urls = {
    "validation": os.environ.get("VALIDATION_URL"),
    "ingestion": os.environ.get("INGESTION_URL"),
    "fhir_converter": os.environ.get("FHIR_CONVERTER_URL"),
    "message_parser": os.environ.get("MESSAGE_PARSER_URL"),
}


def validation_payload(**kwargs) -> dict:
    input = kwargs["input"]
    return {
        "message_type": "ecr",
        "include_error_types": "errors",
        "message": str(input["message"]),
    }


def fhir_converter_payload(**kwargs) -> dict:
    input = kwargs["input"]
    return {
        "input_data": str(input["message"]),
        "input_type": "ecr",
        "root_template": "EICR",
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
            response = post_request(url, payload)
            print(f"Status Code: {response.status_code}")

            if websocket:
                # Write service responses into websocket message
                progress_dict[f"{response.url.split('/')[-1]}"] = {
                    "status_code": response.status_code,
                    "Message": response.reason,
                }

                await websocket.send_text(json.dumps(progress_dict))

            responses[endpoint] = response
        else:
            raise HTTPException(
                status_code=422,
                detail="The Building Block you are attempting to call does not exist:"
                + f" {service}",
            )
    return response, responses
