import io
import json
import logging
import pathlib

from typing import Iterator, IO, Tuple

from azure.identity import DefaultAzureCredential
from azure.storage.blob import ContainerClient


RECORD_TYPE_VXU = "vxu"
RECORD_TYPE_ELR = "elr"
RECORD_TYPE_ECR = "ecr"


def get_blobs(
    container_url: str, container_prefix: str, record_types: list
) -> Iterator[Tuple[str, IO]]:
    """
    Read FHIR bundles from blob storage and return an iterator
    along with the source of the record (one of the RECORD_TYPE_ constants)
    """
    client = get_container_client(container_url)
    for record_type in record_types:
        # record_type is upper-cased in the blob server
        for props in client.list_blobs(
            name_starts_with=container_prefix + record_type.upper()
        ):
            logging.info(f"reading blob {props.name}")
            if props.size > 0:
                # If it's an actual file, download it and yield out the
                # individual records along with record type
                blob_client = client.get_blob_client(props)
                yield (
                    record_type,
                    io.BytesIO(blob_client.download_blob().content_as_bytes()),
                )


def read_bundles_by_type(
    container_url: str, container_prefix: str, record_types: list
) -> Iterator[Tuple[str, dict]]:
    """Reads FHIR bundle dicts using the specified container info
    and returns an iterator referencing tuples containing the
    following information:
    record_type (str) The record type(s) to read,
    corresponding to RECORD_TYPE constants (e.g. elr, ecr, vxu).
    fhir_content (dict) Actual content of the container, json formatted
    """
    for record_type, fp in get_blobs(container_url, container_prefix, record_types):
        for line in fp:
            try:
                yield record_type, json.loads(line)
            except Exception:
                logging.exception("failed to read json contents in line, skipping file")
                break


def get_container_client(url: str):
    """Use whatever creds Azure can find to authenticate with the storage container"""
    creds = DefaultAzureCredential(exclude_shared_token_cache_credential=True)
    return ContainerClient.from_container_url(url, credential=creds)


def write_csvs(url: str, prefix: str, csvs: dict[str, io.StringIO]) -> None:
    """Write the csvs to the final blob storage location"""
    container = get_container_client(url)
    for rtype, contents in csvs.items():
        blob = container.get_blob_client(str(pathlib.Path(prefix) / f"{rtype}.csv"))
        blob.upload_blob(contents.getvalue().encode("utf-8"))
