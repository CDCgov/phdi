from fastapi import APIRouter, Response, status
from pydantic import BaseModel, validator, Field
from typing import Literal, Optional

from app.utils import (
    check_for_fhir_bundle,
    search_for_required_values,
    get_cred_manager,
    StandardResponse,
)

from phdi.fhir.transport import upload_bundle_to_fhir_server

router = APIRouter(
    prefix="/fhir/transport/http",
    tags=["fhir/transport"],
)


class UploadBundleToFhirServerInput(BaseModel):
    bundle: dict = Field(
        description="A FHIR bundle (type 'batch' or 'transaction') to post.  Each entry"
        " in the bundle must contain a `request` element in addition to a `resource`. "
        "The FHIR API provides additional details on creating [FHIR-conformant "
        "batch/transaction](https://hl7.org/fhir/http.html#transaction) bundles."
    )
    cred_manager: Optional[Literal["azure", "gcp"]] = Field(
        description="The credential manager used to authenticate to the FHIR server."
    )
    fhir_url: Optional[str] = Field(
        description="The url of the FHIR server to upload to."
    )

    _check_for_fhir_bundle = validator("bundle", allow_reuse=True)(
        check_for_fhir_bundle
    )


@router.post("/upload_bundle_to_fhir_server", status_code=200)
def upload_bundle_to_fhir_server_endpoint(
    input: UploadBundleToFhirServerInput, response: Response
) -> StandardResponse:
    """
    Upload all of the resources in a FHIR bundle to a FHIR server.

    :param input: A JSON formated request body with schema specified by the
        UploadBundleToFhirServerInput model.
    :return: A dictionary containing the status code and body of the response received
        from the FHIR server.
    """
    input = dict(input)
    required_values = ["cred_manager", "fhir_url"]
    search_result = search_for_required_values(input, required_values)
    if search_result != "All values were found.":
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status_code": "400", "message": search_result}

    input["cred_manager"] = get_cred_manager(
        cred_manager=input["cred_manager"], location_url=input["fhir_url"]
    )

    fhir_server_response = upload_bundle_to_fhir_server(**input)
    fhir_server_response_body = fhir_server_response.json()

    # If the FHIR store responds with a 200 check if any individual resources failed to
    # upload.
    failed_resources = []
    if fhir_server_response.status_code == 200:
        failed_resources = [
            entry
            for entry in fhir_server_response_body["entry"]
            if entry["response"]["status"]
            not in ["200 OK", "201 Created", "200", "201"]
        ]

        fhir_server_response_body = {
            "entry": failed_resources,
            "resourceType": "Bundle",
            "type": "transaction-response",
        }

        if failed_resources != []:
            fhir_server_response.status_code = 400

    status_code = "200"
    if fhir_server_response.status_code != 200:
        response.status_code = status.HTTP_400_BAD_REQUEST
        status_code = "400"

    return {
        "status_code": status_code,
        "message": {
            "fhir_server_response": {
                "fhir_server_status_code": fhir_server_response.status_code,
                "fhir_server_response_body": fhir_server_response_body,
            }
        },
    }
