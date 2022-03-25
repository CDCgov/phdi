import logging
import os
import time

import requests
import azure.functions as func
import json


# The time between polling requests in seconds
POLLING_FREQUENCY = 2.5
POLLING_RETRIES = 120  # 2.5s * 120 retries == 5 min


# def get_access_token() -> str:
#     """Get the access token based on creds in the environment"""
#     tenant_id = os.environ.get("TENANT_ID")
#     url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/token"
#     resp = requests.post(
#         url,
#         data={
#             "grant_type": "client_credentials",
#             "client_id": os.environ.get("CLIENT_ID", ""),
#             "client_secret": os.environ.get("CLIENT_SECRET", ""),
#             "resource": os.environ.get("FHIR_URL", ""),
#         },
#     )

#     if resp.ok and "access_token" in resp.json():
#         return resp.json().get("access_token")

#     logging.error(
#         f"access token request failed status={resp.status_code} message={resp.text}"
#     )
#     raise Exception("access token request failed")


# def poll(url: str, token: str) -> requests.Response:
#     """Poll the given status url until it responds with something other than a 202"""
#     retries = 0
#     while retries < POLLING_RETRIES:
#         resp = requests.get(url, headers={"Authorization": f"Bearer {token}"})

#         # Return out if we've got a valid response *or* it errored out
#         # otherwise keep polling
#         if not resp.ok:
#             logging.error(f"polling failure status={resp.status_code} text={resp.text}")
#             raise Exception("polling failure")

#         if resp.ok and resp.status_code != 202:
#             return resp

#         retries += 1
#         time.sleep(POLLING_FREQUENCY)

#     raise Exception("number of retries exceeded")


def main():

    # try:
    #     token = get_access_token()
    # except Exception:
    #     return func.HttpResponse("error getting access token", status_code=401)

    # url = os.environ.get("FHIR_URL", "")
    # resp = requests.post(
    #     f"{url}/$import",
    #     headers={
    #         "Authorization": f"Bearer {token}",
    #         "Accept": "application/fhir+json",
    #         "Prefer": "respond-async",
    #     },
    # )

    # if resp.ok:
    #     status_url = resp.headers.get("Content-Location")
    #     try:
    #         sresp = poll(status_url, token)
    #         return func.HttpResponse(
    #             sresp.text,
    #             mimetype="application/json",
    #             status_code=sresp.status_code,
    #         )
    #     except Exception:
    #         return func.HttpResponse("export failed", status_code=500)

    # logging.error(
    #     f"error starting export status_code={resp.status_code} message={resp.text}"
    # )
    # return func.HttpResponse("export failed", status_code=resp.status_code)
    read_file("./ExplanationOfBenefit-1.ndjson")

def read_file(file):
    with open(file) as fp:
        for line in fp:
            json_line = json.loads(line)
            resource_type = json_line["resourceType"]
            resource_id   = json_line["id"]
            post_to_fhir(line,resource_type,resource_id)

def post_to_fhir(line,resource_type,resource_id):
    # url = os.environ.get("FHIR_URL", "")
    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6ImpTMVhvMU9XRGpfNTJ2YndHTmd2UU8yVnpNYyIsImtpZCI6ImpTMVhvMU9XRGpfNTJ2YndHTmd2UU8yVnpNYyJ9.eyJhdWQiOiJodHRwczovL3BoZGktcGlsb3QuYXp1cmVoZWFsdGhjYXJlYXBpcy5jb20iLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC9kNDE5ZDhmNy0zYjIwLTQ4NzctYWU2Ny03ZmQxMDBjYTFjZjgvIiwiaWF0IjoxNjQ4MjMxNjAwLCJuYmYiOjE2NDgyMzE2MDAsImV4cCI6MTY0ODIzNTUwMCwiYWlvIjoiRTJaZ1lDamcrUGlpTTlFK2Z0WWV2VHRNUmlmS0FRPT0iLCJhcHBpZCI6ImRmZGJlNjAxLTNkZGEtNDU4ZC1iODQ4LWI3YTA2MGYzMWJkMiIsImFwcGlkYWNyIjoiMSIsImlkcCI6Imh0dHBzOi8vc3RzLndpbmRvd3MubmV0L2Q0MTlkOGY3LTNiMjAtNDg3Ny1hZTY3LTdmZDEwMGNhMWNmOC8iLCJvaWQiOiI3YTQ4YjZlYi00MjlkLTQxNDgtODQ3ZC0zZDJmMGViZjMxOTUiLCJyaCI6IjAuQVZBQTk5Z1oxQ0E3ZDBpdVozX1JBTW9jLU5oNFowX3ZXdHhEb2Ytd2MzSkxsSlZfQUFBLiIsInN1YiI6IjdhNDhiNmViLTQyOWQtNDE0OC04NDdkLTNkMmYwZWJmMzE5NSIsInRpZCI6ImQ0MTlkOGY3LTNiMjAtNDg3Ny1hZTY3LTdmZDEwMGNhMWNmOCIsInV0aSI6Ik5sU1RDcHpqUWtXRTZfcTRkTk96QWciLCJ2ZXIiOiIxLjAifQ.i3Dfux4BcFfnB_fDax520OCCqureWgGVJFHXSa7y0t-uIAdOOfgVpnKmpeydmH7-3VM90Q8sRUfLU0qwjZ56tzgJ9filmSTmEuuousd8uDVPeZDOnL3CnVE727ecce3fzVjPrkWjRylbx9bC8Js0Az_W2liy4qbsbBCQuuu8DfYZV25Moa5DofBg2CE195ysbmOEJKuB2C28uF7x1S7YaELVPZXUlP7UbcY18bIX8D3AoNM4U15ES-aKLQBcmBIWBu4BvaY3x_aweZv01KMi6yZpPn4gTPJ1t272D56A6ayfVFBDk_P0Ww_HrnYFqQXBGLvfXtjonVrv063aRQHMCQ"
    url = "https://phdi-pilot.azurehealthcareapis.com"
    print(line)
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

main()