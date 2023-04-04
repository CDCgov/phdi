from fastapi import FastAPI
from pathlib import Path
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
from psycopg2 import OperationalError, errors
import psycopg2
import os
import sys


# from app.config import get_settings

# Read settings immediately to fail fast in case there are invalid values.
# get_settings()


def run_migrations():
    dbname = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    try:
        connection = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
        )
    except OperationalError as err:
        # pass exception to function
        print_psycopg2_exception(err)

        # set the connection to 'None' in case of error
        connection = None
    if connection is not None:
        try:
            with connection.cursor() as cursor:
                cursor.execute(open("./migrations/tables.ddl", "r").read())
        except errors.InFailedSqlTranroughsaction as err:
            # pass exception to function
            print_psycopg2_exception(err)


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

    run_migrations()

    return {"link_found": False, "updated_bundle": input.fhir_bundle}


# https://kb.objectrocket.com/postgresql/python-error-handling-with-the-psycopg2-postgresql-adapter-645
def print_psycopg2_exception(err):
    # get details about the exception
    err_type, err_obj, traceback = sys.exc_info()

    # get the line number when exception occured
    line_num = traceback.tb_lineno

    # print the connect() error
    print("\npsycopg2 ERROR:", err, "on line number:", line_num)
    print("psycopg2 traceback:", traceback, "-- type:", err_type)

    # psycopg2 extensions.Diagnostics object attribute
    print("\nextensions.Diagnostics:", err.diag)

    # print the pgcode and pgerror exceptions
    print("pgerror:", err.pgerror)
    print("pgcode:", err.pgcode, "\n")
