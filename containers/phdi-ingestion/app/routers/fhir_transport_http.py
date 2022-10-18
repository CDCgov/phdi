from fastapi import APIRouter, Response, status
from pydantic import BaseModel, validator
from typing import Literal, Optional
import os

from app.utils import check_for_fhir_bundle, search_for_required_values

from phdi.cloud.azure import AzureCredentialManager
from phdi.cloud.gcp import GcpCredentialManager
from phdi.fhir.transport import upload_bundle_to_fhir_server

router = APIRouter(
    prefix="/fhir/transport/http",
    tags=["fhir/transport"],
)

credential_managers = {"azure": AzureCredentialManager, "gcp": GcpCredentialManager}


class UploadBundleToFhirServerInput(BaseModel):
    bundle: dict
    credential_manager: Optional[Literal["azure", "gcp"]]
    fhir_url: Optional[str]

    _check_for_fhir_bundle = validator("bundle", allow_reuse=True)(
        check_for_fhir_bundle
    )


@router.post("/upload_bundle", status_code=200)
def upload_bundle_to_fhir_server_endpoint(
    input: UploadBundleToFhirServerInput, response: Response
) -> dict:
    """
    Upload all of the resources in a FHIR bundle to a FHIR server.

    :param input: A JSON formated request body with schema specified by the
        UploadBundleToFhirServerInput model.
    :return: A dictionary containing the status code and body of the response received 
        from the FHIR server.
    """

    input = dict(input)
    required_values = ["credential_manager", "fhir_url"]
    search_result = search_for_required_values(input, required_values)
    if search_result != "All values were found.":
        response.status_code = status.HTTP_400_BAD_REQUEST
        return search_result

    input["credential_manager"] = credential_managers[input["credential_manager"]]

    fhir_server_response = upload_bundle_to_fhir_server(**input)
    fhir_server_response_body = fhir_server_response.json()

    # If the FHIR store responds with a 200 check if any individual resources failed to
    # upload.
    failed_resources = []
    if fhir_server_response.status_code == 200:
        failed_resources = [
            entry
            for entry in fhir_server_response_body["entry"]
            if entry["response"]["status"] not in ["200 OK", "201 Created"]
        ]

        fhir_server_response_body = {
            "entry": failed_resources,
            "resourceType": "Bundle",
            "type": "transaction-response",
        }

        if failed_resources != []:
            fhir_server_response.status_code = 400

    if fhir_server_response.status_code != 200:
        response.status_code = status.HTTP_400_BAD_REQUEST

    return {
        "fhir_server_status_code": fhir_server_response.status_code,
        "fhir_server_response_body": fhir_server_response_body,
    }
