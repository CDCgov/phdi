from app.config import get_settings
from typing import Annotated
from fastapi import Response, status, Body
from pathlib import Path
from phdi.containers.base_service import BaseService
from phdi.linkage import (
    add_person_resource,
    link_record_against_mpi,
    DIBBS_BASIC,
    DIBBS_ENHANCED,
)
from pydantic import BaseModel, Field
from typing import Optional
from app.utils import read_json_from_assets, run_migrations, get_settings
from phdi.linkage.mpi import DIBBsMPIConnectorClient

# Ensure MPI is configured as expected.
run_migrations()
settings = get_settings()
MPI_CLIENT = DIBBsMPIConnectorClient(
    pool_size=settings["connection_pool_size"],
    max_overflow=settings["connection_pool_max_overflow"],
)
# Instantiate FastAPI via PHDI's BaseService class
app = BaseService(
    service_name="DIBBs Record Linkage Service",
    description_path=Path(__file__).parent.parent / "description.md",
    include_health_check_endpoint=False,
).start()


# Request and response models
class LinkRecordInput(BaseModel):
    """
    Schema for requests to the /link-record endpoint.
    """

    bundle: dict = Field(
        description="A FHIR bundle containing a patient resource to be checked "
        "for links to existing patient records"
    )
    use_enhanced: Optional[bool] = Field(
        description="Optionally, a boolean flag indicating whether to use the "
        "DIBBs enhanced algorithm (with statistical correction) for record linkage. "
        "If `False` and no optional `algo_config` is provided, the service will use "
        "the DIBBs basic algorithm. If this parameter is set to `True`, the enhanced "
        "algorithm will be used in place of any configuration supplied in "
        "`algo_config`.",
        default=False,
    )
    algo_config: Optional[dict] = Field(
        description="A JSON dictionary containing the specification for a "
        "linkage algorithm, as defined in the SDK functions `read_algo_config` "
        "and `write_algo_config`. Default value uses the DIBBS in-house basic "
        "algorithm.",
        default={},
    )
    external_person_id: Optional[str] = Field(
        description="The External Identifier, provided by the client,"
        " for a unique patient/person that is linked to patient(s)",
        default=None,
    )


class LinkRecordResponse(BaseModel):
    """
    The schema for responses from the /link-record endpoint.
    """

    found_match: bool = Field(
        description="A true value indicates that one or more existing records "
        "matched with the provided record, and these results have been linked."
    )
    updated_bundle: dict = Field(
        description="If link_found is true, returns the FHIR bundle with updated"
        " references to existing Personresource. If link_found is false, "
        "returns the FHIR bundle with a reference to a newly created "
        "Person resource."
    )
    message: Optional[str] = Field(
        description="An optional message in the case that the linkage endpoint did "
        "not run successfully containing a description of the error that happened.",
        default="",
    )


class HealthCheckResponse(BaseModel):
    """
    The schema for response from the record linkage health check endpoint.
    """

    status: str = Field(description="Returns status of this service")

    mpi_connection_status: str = Field(
        description="Returns status of connection to Master Patient Index(MPI)"
    )


@app.get("/")
async def health_check() -> HealthCheckResponse:
    """
    Check the status of this service and its connection to Master Patient Index(MPI). If
    an HTTP 200 status code is returned along with '{"status": "OK"}' then the record
    linkage service is available and running properly. The mpi_connection_status field
    contains a description of the connection health to the MPI database.
    """

    try:
        mpi_client = DIBBsMPIConnectorClient()  # noqa: F841
    except Exception as err:
        return {"status": "OK", "mpi_connection_status": str(err)}
    return {"status": "OK", "mpi_connection_status": "OK"}


# Sample requests and responses for docs
sample_link_record_requests = read_json_from_assets("sample_link_record_requests.json")
sample_link_record_responses = read_json_from_assets(
    "sample_link_record_responses.json"
)


@app.post(
    "/link-record", status_code=200, responses={200: sample_link_record_responses}
)
async def link_record(
    input: Annotated[LinkRecordInput, Body(examples=sample_link_record_requests)],
    response: Response,
) -> LinkRecordResponse:
    """
    Compare a FHIR bundle with records in the Master Patient Index (MPI) to
    check for matches with existing patient records If matches are found,
    returns the bundle with updated references to existing patients.
    """

    input = dict(input)
    input_bundle = input.get("bundle", {})
    external_id = input.get("external_person_id", None)

    # Check that DB type is appropriately set up as Postgres so
    # we can fail fast if it's not
    db_type = get_settings().get("mpi_db_type", "")
    if db_type != "postgres":
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return {
            "found_match": False,
            "updated_bundle": input_bundle,
            "message": f"Unsupported database type {db_type} supplied. "
            + "Make sure your environment variables include an entry "
            + "for `mpi_db_type` and that it is set to 'postgres'.",
        }

    # Determine which algorithm to use; default is DIBBS basic
    # Check for enhanced algo before checking custom algo
    use_enhanced = input.get("use_enhanced", False)
    if use_enhanced:
        algo_config = DIBBS_ENHANCED
    else:
        algo_config = input.get("algo_config", {}).get("algorithm", [])
        if algo_config == []:
            algo_config = DIBBS_BASIC

    # Now extract the patient record we want to link
    try:
        record_to_link = [
            entry.get("resource")
            for entry in input_bundle.get("entry", [])
            if entry.get("resource", {}).get("resourceType", "") == "Patient"
        ][0]
    except IndexError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "found_match": False,
            "updated_bundle": input_bundle,
            "message": "Supplied bundle contains no Patient resource to link on.",
        }

    # Now link the record
    try:
        (found_match, new_person_id) = link_record_against_mpi(
            record=record_to_link,
            algo_config=algo_config,
            external_person_id=external_id,
            mpi_client=MPI_CLIENT,
        )
        updated_bundle = add_person_resource(
            new_person_id, record_to_link.get("id", ""), input_bundle
        )
        return {"found_match": found_match, "updated_bundle": updated_bundle}

    except ValueError as err:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "found_match": False,
            "updated_bundle": input_bundle,
            "message": f"Could not connect to database: {err}",
        }
