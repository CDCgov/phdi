import io
import json

from typing import Iterable

from azure.storage.blob import ContainerClient


def get_patient_records(conn_str: str, container_name: str) -> Iterable[dict]:
    """
    Given an bucket connection string and a container name,
    yield all of the patient records in the container
    """
    conn = ContainerClient.from_connection_string(
        conn_str=conn_str, container_name=container_name
    )

    # Go through all the matching files and yield the patient records
    for props in conn.list_blobs(name_starts_with="Patient"):
        client = conn.get_blob_client(props)
        buf = io.BytesIO(client.download_blob().content_as_bytes())

        for line in buf:
            yield json.loads(line)
