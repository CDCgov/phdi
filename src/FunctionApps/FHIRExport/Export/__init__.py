import logging
import os
import time

import requests
import azure.functions as func


# The time between polling requests in seconds
POLLING_FREQUENCY = 2.5
POLLING_RETRIES = 120  # 2.5s * 120 retries == 5 min


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


def poll(url: str, token: str) -> requests.Response:
    """Poll the given status url until it responds with something other than a 202"""
    retries = 0
    while retries < POLLING_RETRIES:
        resp = requests.get(url, headers={"Authorization": f"Bearer {token}"})

        # Return out if we've got a valid response *or* it errored out
        # otherwise keep polling
        if not resp.ok:
            logging.error(f"polling failure status={resp.status_code} text={resp.text}")
            raise Exception("polling failure")

        if resp.ok and resp.status_code != 202:
            return resp

        retries += 1
        time.sleep(POLLING_FREQUENCY)

    raise Exception("number of retries exceeded")


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
        status_url = resp.headers.get("Content-Location")
        try:
            sresp = poll(status_url, token)
            return func.HttpResponse(
                sresp.text,
                mimetype="application/json",
                status_code=sresp.status_code,
            )
        except Exception:
            return func.HttpResponse("export failed", status_code=500)

    logging.error(
        f"error starting export status_code={resp.status_code} message={resp.text}"
    )
    return func.HttpResponse("export failed", status_code=resp.status_code)
