from fastapi import APIRouter, Response, status
from pydantic import BaseModel
from typing import Literal, Optional

from app.utils import (
    search_for_required_values,
    get_cloud_provider_storage_connection
)


router = APIRouter(
    prefix="/cloud/storage/write",
    tags=["cloud/storage"],
)


class WriteBlobToStorageInput(BaseModel):
    blob: dict
    cloud_provider: Optional[Literal["azure", "gcp"]]
    bucket_name: Optional[str]
    file_name: Optional[str]


@router.post("/write_blob_to_cloud_storage", status_code=200)
def write_blob_to_cloud_storage_endpoint(
    input: WriteBlobToStorageInput, response: Response
) -> dict:
    """
    Upload the information from a blob into a specified cloud providers storage
    organizing it by a bucket name as well as a file name.

    :param input: A JSON formated request body (blob) with schema specified by the
        WriteBlobToStorageInput model.
    :return: A dictionary containing the status code and body of the response received
        from the cloud provider.
    """
    input = dict(input)
    required_values = ["cloud_provider", "bucket_name", "file_name"]
    search_result = search_for_required_values(input, required_values)
    if search_result != "All values were found.":
        response.status_code = status.HTTP_400_BAD_REQUEST
        return search_result

    cloud_provider_connection = get_cloud_provider_storage_connection(
        cloud_provider=input["cloud_provider"]
    )

    cloud_provider_connection.upload_object(
        message=input,
        container_name=input["bucket_name"],
        filename=input["file_name"],
    )

    response.status_code = status.HTTP_201_CREATED
    return {
        "message": "The data has successfully been stored in the {} cloud in {} container with the name {}.".format(
            input["cloud_provider"], input["bucket_name"], input["file_name"]
        )
    }
