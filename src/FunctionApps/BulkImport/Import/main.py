import logging
import os
import time

import requests
import azure.functions as func
import json

def main():
    try:
        token = get_access_token()
    except Exception:
        return func.HttpResponse("error getting access token", status_code=401)
    
    read_file("./ExplanationOfBenefit-1.ndjson",token)

def read_file(file,token):
    with open(file) as fp:
        for line in fp:
            print("IN READ FILE")
            json_line = json.loads(line)
            resource_type = json_line["resourceType"]
            resource_id   = json_line["id"]
            post_to_fhir(line,resource_type,resource_id,token)

def post_to_fhir(line,resource_type,resource_id,token):
    print("IN POST TO FHIR")
    url = os.environ.get("FHIR_URL", "")
    print(url)
    # url = "https://phdi-pilot.azurehealthcareapis.com"
    try:
        resp = requests.post(
            f"{url}/{resource_type}",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/fhir+json",
                "Content-type": "application/json"
            },
            data=line
        )
        print(resp)
    except Exception:
            return func.HttpResponse("ndjson to fhir import failed", status_code=500)
    logging.error(
        f"Failed to import ndjson to FHIR server failed status={resp.status_code} message={resp.text}"
    )

def get_access_token() -> str:
    """Get the access token based on creds in the environment"""
    tenant_id = os.environ.get("TENANT_ID")
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/token"
    resp = requests.post(
        url,
        data={
            "grant_type": "client_credentials",
            "client_id": os.environ.get("CLIENT_ID", ""),
            "client_secret": os.environ.get("CLIENT_SECRET", ""),
            "resource": os.environ.get("FHIR_URL", ""),
        },
    )

    if resp.ok and "access_token" in resp.json():
        return resp.json().get("access_token")

    logging.error(
        f"access token request failed status={resp.status_code} message={resp.text}"
    )
    raise Exception("access token request failed")

main()