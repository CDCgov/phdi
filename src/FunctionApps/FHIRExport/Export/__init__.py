import logging
import os

import requests
import azure.functions as func


def get_access_token():
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


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        token = get_access_token()
    except Exception:
        return func.HttpResponse("error getting access token", status_code=401)

    url = os.environ.get("FHIR_URL", "")
    resp = requests.get(
        f"{url}/$export",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/fhir+json",
            "Prefer": "respond-async",
        },
    )

    if resp.ok:
        return func.HttpResponse("export started", status_code=resp.status_code)

    logging.error(
        f"error starting export status_code={resp.status_code} message={resp.text}"
    )
    return func.HttpResponse("export failed", status_code=resp.status_code)
