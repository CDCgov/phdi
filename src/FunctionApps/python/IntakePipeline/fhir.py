import io
import json
import logging

from typing import Iterator, IO

from azure.identity import DefaultAzureCredential
from azure.storage.blob import ContainerClient


def get_blob_client(container_url: str) -> ContainerClient:
    """Use whatever creds Azure can find to authenticate with the storage container"""
    creds = DefaultAzureCredential()
    return ContainerClient.from_container_url(container_url, credential=creds)


def get_blobs(container_url: str, container_prefix: str) -> Iterator[IO]:
    """Grabs blob files from the container as a readable file-like iterator"""
    client = get_blob_client(container_url)
    for props in client.list_blobs(name_starts_with=container_prefix):
        if props.size > 0:
            # If it's an actual file, download it and yield out the individual records
            blob_client = client.get_blob_client(props)
            yield io.BytesIO(blob_client.download_blob().content_as_bytes())
    return


def read_fhir_bundles(container_url: str, container_prefix: str) -> Iterator[dict]:
    """Reads FHIR bundle dicts from Azure blob storage as an iterator"""
    for fp in get_blobs(container_url, container_prefix):
        for line in fp:
            try:
                yield json.loads(line)
            except Exception:
                logging.exception("failed to read json contents in line, skipping file")
                break


def upload_bundle_to_fhir_server(bundle: dict) -> None:
    pass
