import io
import pathlib

from typing import Iterator, Tuple

from azure.identity import DefaultAzureCredential
from azure.storage.blob import ContainerClient


RECORD_TYPE_VXU = "vxu"
RECORD_TYPE_ELR = "elr"
RECORD_TYPE_ECR = "ecr"


def read_bundles_by_type() -> Iterator[Tuple[str, dict]]:
    """
    Read FHIR bundles from blob storage and return an iterator
    along with the source of the record (one of the RECORD_TYPE_ constants)
    """

    return


def get_container_client(url: str):
    """TODO: refactor with IntakePipeline.fhir"""
    creds = DefaultAzureCredential()
    return ContainerClient.from_container_url(url, credential=creds)


def write_csvs(url: str, prefix: str, csvs: dict[str, io.StringIO]) -> None:
    """Write the csvs to the final blob storage location"""
    container = get_container_client(url)
    for rtype, contents in csvs.items():
        blob = container.get_blob_client(str(pathlib.Path(prefix) / f"{rtype}.csv"))
        blob.upload_blob(contents.getvalue().encode("utf-8"))
