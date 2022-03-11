"""
Function to exercise infrastructure from the inside.

Query parameters:

* `run_azure` (default: true) - if 'false' we won't try to interact with the storage account or key vault

Headers:

* `Accept` if 'text/plain' we'll return a plaintext response, otherwise it'll be JSON
"""  # noqa: E501
import collections
import json
import logging
import os
import re
import socket

import azure.functions as func
import azure.identity
import azure.keyvault.secrets
import requests
from azure.storage.blob import BlobServiceClient


logger = logging.getLogger(__name__)

KEY_VAULT_NAME = "pitest-app-kv"
SECRET_NAME = "test-secret"
SECRET_VALUE_EXPECTED = "BurritoTown"
STORAGE_ACCOUNT_CONNECTION = os.environ.get("APPSETTING_AzureWebJobsStorage")
STORAGE_FILENAME = "_test.txt"
STORAGE_HOST = "pitestdatasa.privatelink.blob.core.windows.net"
URL_IP_CHECK = "https://api.ipify.org/?format=json"

Check = collections.namedtuple("Check", ["name", "status", "message"])


def is_blank(v):
    return v is None or v.strip() == ""


def verify_blob_storage():
    checks = []
    try:
        service_client = BlobServiceClient.from_connection_string(
            STORAGE_ACCOUNT_CONNECTION
        )
        checks.append(Check("Storage client", "ok", "Created from connection string"))
    except Exception as e:
        return [
            Check("Storage client", "error", f"Failed to create BlobServiceClient: {e}")
        ]

    containers = ["bronze", "silver", "gold"]

    for container_name in containers:
        try:
            container_client = service_client.get_container_client(container_name)
        except Exception as e:
            checks.append(
                Check(
                    f"Container client: {container_name}",
                    "error",
                    f"Failed to create container client: {e}",
                )
            )
            continue

        try:
            blob_client = container_client.get_blob_client(STORAGE_FILENAME)
        except Exception as e:
            checks.append(
                Check(
                    f"Blob client: {container_name}",
                    "error",
                    f"Failed to create blob client: {e}",
                )
            )
            continue

        try:
            blob = blob_client.download_blob()
            blob_value = blob.content_as_text()
            checks.append(Check(f"Blob download: {container_name}", "ok", ""))
        except Exception as e:
            checks.append(
                Check(
                    f"Blob read: {container_name}", "error", f"Failed to get blob: {e}"
                )
            )
            continue

        # Contents look like this -- we'll increment the number after 'Count: ':
        # # This test is to ensure we can read/write to blob storage
        # Count: 0
        try:
            lines = blob_value.split("\n")
            _, count = lines[1].strip().split(" ")
            new_count = int(count.strip()) + 1
            new_value = "\n".join([lines[0], f"Count: {new_count}"])
            blob_client.upload_blob(new_value, overwrite=True)
            checks.append(Check(f"Blob upload: {container_name}", "ok", ""))
        except Exception as e:
            checks.append(
                Check(
                    f"Blob upload: {container_name}",
                    "error",
                    f"Failed to uploadblob: {e}",
                )
            )

    return checks


def verify_dns():
    checks = []
    try:
        google_ip = socket.gethostbyname("google.com")
        checks.append(
            Check(
                "DNS lookup - external", "ok", f'Found IP "{google_ip}" for google.com'
            )
        )
    except Exception as e:
        checks.append(Check("DNS lookup - external", "error", str(e)))

    try:
        storage_ip = socket.gethostbyname(STORAGE_HOST)
        checks.append(
            Check(
                "DNS lookup - internal",
                "ok",
                f'Found IP "{storage_ip}" for "{STORAGE_HOST}"',
            )
        )
    except Exception as e:
        checks.append(Check("DNS lookup - internal", "error", str(e)))

    return checks


def verify_key_vault_read():
    url = f"https://{KEY_VAULT_NAME}.vault.azure.net"
    try:
        credential = azure.identity.DefaultAzureCredential()
        client = azure.keyvault.secrets.SecretClient(
            vault_url=url, credential=credential
        )
        secret = client.get_secret(SECRET_NAME).value
        if secret == SECRET_VALUE_EXPECTED:
            return Check("Key vault", "ok", "Fetched secret and verified contents")
        else:
            return Check(
                "Key vault",
                "error",
                f"Fetched secret ok but value mismatch "
                f"(expected {SECRET_VALUE_EXPECTED}, got {secret}",
            )

    except Exception as e:
        return Check(
            "Key vault", "error", f"Failed to create client or fetch secret: {e}"
        )


def verify_my_ip():
    try:
        response = requests.get(URL_IP_CHECK, timeout=10)
        ip = response.json().get("ip") or "Unknown IP"
        return Check("IP Check", "ok", ip)
    except Exception as e:
        return Check("IP Check", "error", str(e))


def main(req: func.HttpRequest) -> func.HttpResponse:
    logger.info("APP: Python HTTP trigger function processing a request.")
    checks = []

    logger.info("Task 1: Verifying DNS")
    checks.extend(
        verify_dns()
    )  # task 1: can I lookup IPs? checks whether the DNS from CDC (or Azure) is working
    logger.info("Task 2: Verifying my IP")
    checks.append(
        verify_my_ip()
    )  # task 2: can I reach the internet? if so, what is my IP?

    # ?run_azure=false will skip the storage account and key vault actions
    run_azure = req.params.get("run_azure", "true").strip().lower() == "true"

    if run_azure:
        logger.info("Task 3: Verifying blob storage")
        if is_blank(STORAGE_ACCOUNT_CONNECTION):
            checks.append(Check("Blob *", "error", "No connection string defined"))
        else:
            checks.extend(
                verify_blob_storage()
            )  # task 3: can I read/write to blob storage?
        logger.info("Task 4: Verifying key vault")
        checks.append(verify_key_vault_read())  # task 4: can I read from key vault?
    else:
        logger.info("Task 3+4: Skipping on request")
        checks.append(Check("Blob *", "skip", "Instructed to not run azure tasks"))
        checks.append(Check("Key vault", "skip", "Instructed to not run azure tasks"))

    # just check the first one rather than dealing with q-weights
    accept_header = re.split(r"\s+,\s+", req.headers.get("Accept", ""))
    is_text = len(accept_header) > 0 and "text" in accept_header[0]

    if is_text:
        headers = {"Content-Type": "text/plain"}
        body = "Checks:\n"
        for c in checks:
            body += f"* {c.name}: {c.status}"
            if c.message != "":
                body += f" - {c.message}"
            body += "\n"

        body += "\nEnvironment:\n"
        for k in sorted(os.environ.keys()):
            body += f"{k}={os.environ[k]}\n"

    else:
        response = {
            "checks": [c._asdict() for c in checks],
            "env": {k: v for k, v in os.environ.items()},
        }
        body = json.dumps(response, indent=4, sort_keys=True)
        headers = {"Content-Type": "application/json"}

    return func.HttpResponse(body=body, headers=headers, status_code=200)
