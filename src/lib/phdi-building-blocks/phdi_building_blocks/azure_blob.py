import json
import pathlib
from azure.identity import DefaultAzureCredential
from azure.storage.blob import ContainerClient


def get_blob_client(container_url: str) -> ContainerClient:
    """Use whatever creds Azure can find to authenticate with the storage container"""
    creds = DefaultAzureCredential()
    return ContainerClient.from_container_url(container_url, credential=creds)


def store_data(
    container_url: str,
    prefix: str,
    filename: str,
    bundle_type: str,
    message_json: dict = None,
    message: str = None,
) -> None:
    """
    Store the given data, which is either a FHIR bundle or an HL7 message in the
    appropriate output container
    """
    client = get_blob_client(container_url)
    blob = client.get_blob_client(str(pathlib.Path(prefix) / bundle_type / filename))
    if message_json is not None:
        blob.upload_blob(json.dumps(message_json).encode("utf-8"), overwrite=True)
    elif message is not None:
        blob.upload_blob(bytes(message, "utf-8"), overwrite=True)
