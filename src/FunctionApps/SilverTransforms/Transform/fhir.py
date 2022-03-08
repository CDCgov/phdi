import io
import json

from typing import Iterable

from azure.storage.blob import ContainerClient


def get_patient_records(conn_str: str, container_name: str) -> Iterable[dict]:
    """
    Given a bucket connection string and a container name,
    yield all of the patient records in the container
    """
    client = ContainerClient.from_connection_string(
        conn_str=conn_str, container_name=container_name
    )

    # Go through all the matching files and yield the patient records
    for props in client.list_blobs(name_starts_with="Patient"):
        blob_client = client.get_blob_client(props)
        buf = io.BytesIO(blob_client.download_blob().content_as_bytes())

        for line in buf:
            yield json.loads(line)


def write_patient_records(conn_str: str, container_name: str, patients: list[dict]):
    """
    Write patient records to a new blob in the silver container
    Eventually:
        * Write to multiple files (ie: split after x records, size, etc)
        * Add some identifying info to the output files
    """
    client = ContainerClient.from_connection_string(
        conn_str=conn_str, container_name=container_name
    )

    # Convert the patients to ndjson and write it
    buf = "\n".join([json.dumps(p) for p in patients])
    return client.upload_blob("patients.ndjson", buf, overwrite=True)
