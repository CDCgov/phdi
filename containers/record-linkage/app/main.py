from fastapi import FastAPI
from pathlib import Path
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
import psycopg2
import os

# from app.config import get_settings

# Read settings immediately to fail fast in case there are invalid values.
# get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    dbname = os.getenv("DB_NAME", "testdb")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "pw")
    host = os.getenv("DB_HOST", "db")

    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
    )
    with conn.cursor() as cur:
        cur.execute(open("./migrations/tables.ddl", "r").read())
    yield


# Instantiate FastAPI and set metadata.
description = Path("description.md").read_text(encoding="utf-8")
app = FastAPI(
    title="DIBBs Record Linkage Service",
    version="0.0.1",
    contact={
        "name": "CDC Public Health Data Infrastructure",
        "url": "https://cdcgov.github.io/phdi-site/",
        "email": "dmibuildingblocks@cdc.gov",
    },
    license_info={
        "name": "Creative Commons Zero v1.0 Universal",
        "url": "https://creativecommons.org/publicdomain/zero/1.0/",
    },
    description=description,
    lifespan=lifespan,
)


# Request and and response models
class LinkRecordInput(BaseModel):
    """
    Schema for requests to the /link-record endpoint.
    """

    fhir_bundle: dict = Field(
        description="A FHIR bundle containing a patient resource to be checked "
        "for links to existing patient records"
    )


class LinkRecordResponse(BaseModel):
    """
    The schema for responses from the /link-record endpoint.
    """

    link_found: bool = Field(
        description="A true value indicates linked record(s) were found."
    )
    updated_bundle: dict = Field(
        description="If link_found is true, returns the FHIR bundle with updated"
        " references to existing Personresource. If link_found is false, "
        "returns the FHIR bundle with a reference to a newly created "
        "Person resource."
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
    contains a description of the connection health to the
    MPI database.
    """
    return {"status": "OK", "mpi_connection_status": "Stubbed response"}


@app.post("/link-record", status_code=200)
async def link_record(input: LinkRecordInput) -> LinkRecordResponse:
    """
    This is just a stub.
    Compare a FHIR bundle with records in the Master Patient Index (MPI) to
    check for matches with existing patient records If matches are found,
    returns the bundle with updated references to existing patients.
    :param input: A JSON formatted request body with schema specified by the
        LinkRecordInput model.
    :return: A JSON formatted response body with schema specified by the
        LinkRecordResponse model.
    """

    return {"link_found": False, "updated_bundle": input.fhir_bundle}
