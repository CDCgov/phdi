import logging

import azure.functions as func
import os
import json
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from smartystreets_python_sdk import StaticCredentials, exceptions, ClientBuilder
from smartystreets_python_sdk.us_street import Lookup as StreetLookup

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    key_vault_name = os.environ["KEY_VAULT_NAME"]
    kv_uri = f"https://{key_vault_name}.vault.azure.net"
    azure_credential = DefaultAzureCredential()
    client = SecretClient(vault_url=kv_uri, credential=azure_credential)

    ss_auth_id = client.get_secret("SmartyStreetsAuthID").value
    ss_auth_token = client.get_secret("SmartyStreetsAuthToken").value
    logging.info(f"Acquired credentials from Key Vault: {ss_auth_id}, {ss_auth_token}")

    ss_credentials = StaticCredentials(ss_auth_id, ss_auth_token)
    ss_client = (
        ClientBuilder(ss_credentials)
        .with_licenses(["us-standard-cloud"])
        .build_us_street_api_client()
    )

    address = req.params.get("address")
    logging.info(f"Passed address: {address}")

    if not address:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            address = req_body.get("address")

    if address:
        lookup = StreetLookup()
        lookup.street = address
        try:
            logging.info(f"Sending lookup: {lookup}")
            ss_client.send_lookup(lookup)

            response = {}
            response["input"] = address
            results = []
            for result in lookup.result:
                result_info = {
                    "Delivery_line_1" : result.delivery_line_1,
                    "Delivery_line_2" : result.delivery_line_2,
                    "last_line" : result.last_line,
                    "primary_number":  result.components.primary_number,
                    "pre_direction":	result.components.street_predirection,
                    "street_name":	    result.components.street_name,
                    "street_suffix":   result.components.street_suffix,
                    "post_direction":   result.components.street_postdirection,
                    "city" : result.components.city_name,
                    "state": result.components.state_abbreviation,
                    "county": result.metadata.county_name,
                    "zip": result.components.zipcode,
                    "lat": result.metadata.latitude,
                    "lng": result.metadata.longitude
                }
                results.append(result_info)
            response["results"] = results
            logging.info(f"Lookup sent.")

            return func.HttpResponse(
                json.dumps(response),
                    mimetype="application/json",
                )
        except exceptions.SmartyException as err:
            logging.error(f"Encountered error: {err}")
            return func.HttpResponse(f"Error: {err}", status_code=400)
    else:
        return func.HttpResponse(
            "This HTTP triggered function executed successfully. Pass an address in the query string or in the request body for a personalized response.",
            status_code=200,
        )
