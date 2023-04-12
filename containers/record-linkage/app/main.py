from app.config import get_settings
from fastapi import FastAPI, Response, status
from pathlib import Path
from phdi.linkage import (
    add_person_resource,
    link_record_against_mpi,
    read_linkage_config,
    DIBBsConnectorClient,
)
from pydantic import BaseModel, Field
from psycopg2 import OperationalError, errors
from typing import Optional
import psycopg2
import os
import sys


def run_migrations():
    dbname = os.getenv("mpi_dbname")
    user = os.getenv("mpi_user")
    password = os.getenv("mpi_password")
    host = os.getenv("mpi_host")
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

    bundle: dict = Field(
        description="A FHIR bundle containing a patient resource to be checked "
        "for links to existing patient records"
    )
    algo_config: Optional[dict] = Field(
        description="A JSON dictionary containing the specification for a "
        "linkage algorithm, as defined in the SDK functions `read_algo_config` "
        "and `write_algo_config`. Default value uses the DIBBS in-house basic "
        "algorithm.",
        default={},
    )
    db_type: Optional[str] = Field(
        description="A database type of the particular "
        "MPI to link against, such as postgres. Default is postgres.",
        default="postgres",
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
    run_migrations()
    try:
        dbname = get_settings().get("mpi_dbname")
        user = get_settings().get("mpi_user")
        password = get_settings().get("mpi_password")
        host = get_settings().get("mpi_host")
        port = get_settings().get("mpi_port")
        patient_table = get_settings().get("mpi_patient_table")
        person_table = get_settings().get("mpi_person_table")
        db_client = DIBBsConnectorClient(
            dbname, user, password, host, port, patient_table, person_table
        )
        db_client.connection = psycopg2.connect(
            dbname=db_client.database,
            user=db_client.user,
            password=db_client.password,
            host=db_client.host,
            port=db_client.port,
        )
    except OperationalError as err:
        return {"status": "OK", "mpi_connection_status": str(err)}
    except ValueError as err:
        return {"status": "OK", "mpi_connection_status": str(err)}
    return {"status": "OK", "mpi_connection_status": "OK"}


@app.post("/link-record", status_code=200)
async def link_record(input: LinkRecordInput, response: Response) -> LinkRecordResponse:
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
    input = dict(input)

    # Determine which algorithm to use
    # Default is DIBBS basic, which comes prepacked in the SDK
    algo_config = input.get("algo_config", {}).get("algorithm", [])
    if algo_config == []:
        algo_config = read_linkage_config(
            Path(__file__).parent.parent.parent.parent
            / "phdi"
            / "linkage"
            / "algorithms"
            / "dibbs_basic.json"
        )

    # Now extract the patient records we want to link
    # Bundle most likely contains 1, but fetch them "all" just in case
    input_bundle = input.get("bundle", {})
    try:
        record_to_link = [
            r.get("resource")
            for r in input_bundle.get("entry", [])
            if r.get("resource", {}).get("resourceType", "") == "Patient"
        ][0]
    except IndexError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "found_match": False,
            "updated_bundle": input_bundle,
            "message": "Supplied bundle contains no Patient resource to link on.",
        }

    # Initialize a DB connection for use with the MPI
    db_type = input.get("db_type")
    if db_type == "postgres":
        try:
            dbname = get_settings().get("mpi_dbname")
            user = get_settings().get("mpi_user")
            password = get_settings().get("mpi_password")
            host = get_settings().get("mpi_host")
            port = get_settings().get("mpi_port")
            patient_table = get_settings().get("mpi_patient_table")
            person_table = get_settings().get("mpi_person_table")

            # Link the record and add new person information
            db_client = DIBBsConnectorClient(
                dbname, user, password, host, port, patient_table, person_table
            )
            (found_match, new_person_id) = link_record_against_mpi(
                record_to_link, algo_config, db_client
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
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "found_match": False,
            "updated_bundle": input_bundle,
            "message": f"Unsupported database type {db_type} supplied.",
        }


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
