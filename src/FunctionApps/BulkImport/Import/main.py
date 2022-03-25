import logging
import os
import time

import requests
import azure.functions as func
import json
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def main():
    try:
        token = get_access_token()
    except Exception:
        return func.HttpResponse("error getting access token", status_code=401)
    
    read_file("./ExplanationOfBenefit-1.ndjson",token)

def read_file(file,token):
    with open(file) as fp:
        for line in fp:
            json_line = json.loads(line)
            resource_type = json_line["resourceType"]
            resource_id   = json_line["id"]
            post_to_fhir(line,resource_type,resource_id,token)

def post_to_fhir(line,resource_type,resource_id,token):
    retry_strategy = Retry(
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "POST", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)
    url = os.environ.get("FHIR_URL", "")
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
        print(f"status={resp.status_code} message={resp.text}")
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





