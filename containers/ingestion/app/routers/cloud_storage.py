from typing import Literal
from typing import Optional

from fastapi import APIRouter
from fastapi import Response
from fastapi import status
from pydantic import BaseModel
from pydantic import Field

from app.utils import get_cloud_provider_storage_connection
from app.utils import search_for_required_values
from app.utils import StandardResponse

router = APIRouter(
    prefix="/cloud/storage",
    tags=["cloud/storage"],
)


class WriteBlobToStorageInput(BaseModel):
    blob: dict = Field(description="Contents of a blob to be written to cloud storage.")
    cloud_provider: Optional[Literal["azure", "gcp"]] = Field(
        description="The cloud provider hosting the storage resource that the blob will"
        " be uploaded to. Must be provided in the request body or set as an environment"
        " variable of the service."
    )
    bucket_name: Optional[str] = Field(
        description="Name of the cloud storage bucket that the blob should be uploaded "
        "to. Must be provided in the request body or set as an environment variable of "
        "the service."
    )
    file_name: str = Field(description="Name of the blob")
    storage_account_url: Optional[str] = Field(
        description="The URL of an Azure storage account. Must be provided in the "
        "request body or set as an environment variable of the service is "
        "'cloud_provider' is 'azure'.",
        default="",
    )


@router.post("/write_blob_to_storage", status_code=201)
def write_blob_to_cloud_storage_endpoint(
    input: WriteBlobToStorageInput, response: Response
) -> StandardResponse:
    """
    This endpoint uploads the information from a blob into a specified cloud
    provider's storage organizing it by a bucket name as well as a file name.

    ### Inputs and Outputs
    - :param input: A JSON formatted request body (blob) with schema specified by the
        WriteBlobToStorageInput model.
    - :return: A dictionary containing the status code and body of the response received
        from the cloud provider.
    """
    input = dict(input)
    required_values = ["cloud_provider", "bucket_name"]
    search_result = search_for_required_values(input, required_values)
    if search_result != "All values were found.":
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status_code": 400, "message": search_result}
    if input["cloud_provider"] == "azure":
        azure_required_values = ["storage_account_url"]
        azure_search_result = search_for_required_values(
            input, required_values=azure_required_values
        )
        if azure_search_result != "All values were found.":
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"status_code": 400, "message": azure_search_result}

    cloud_provider_connection = get_cloud_provider_storage_connection(
        cloud_provider=input["cloud_provider"],
        storage_account_url=input["storage_account_url"],
    )

    full_file_name = input["file_name"]
    cloud_provider_connection.upload_object(
        message=input["blob"],
        container_name=input["bucket_name"],
        filename=full_file_name,
    )

    response.status_code = status.HTTP_201_CREATED
    return {
        "status_code": "201",
        "message": (
            "The data has successfully been stored "
            "in the {} cloud in {} container with the name {}.".format(
                input["cloud_provider"], input["bucket_name"], full_file_name
            )
        ),
    }
