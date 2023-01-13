from fastapi import FastAPI, Response, status
from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
import urllib.parse
import datetime
import jsonschema
from pathlib import Path
from phdi.cloud.core import BaseCredentialManager
from phdi.tabulation import validate_schema
from phdi.tabulation.tables import write_data
from phdi.fhir.tabulation.tables import (
    _generate_search_urls,
    extract_data_from_fhir_search_incremental,
    tabulate_data,
)
from app.config import get_settings
from app.utils import (
    get_cred_manager,
    search_for_required_values,
    check_schema_validity,
)

# Read settings from environmnent.
get_settings()

# Instantiate FastAPI and set metadata.
description = Path("description.md").read_text(encoding="utf-8")
app = FastAPI(
    title="PHDI Tabulation Service",
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


class SchemaValidationInput(BaseModel):
    """
    Input parameters for schema validation.
    """

    table_schema: dict = Field(
        alias="schema", description="A JSON formatted PHDI schema."
    )


class TabulateInput(BaseModel):
    """
    Request schema for the tabulate endpoint.
    """

    schema_: dict = Field(alias="schema", description="A JSON formatted PHDI schema.")
    output_type: Literal["parquet", "csv", "sql"] = Field(
        description="Method for persisting data after extraction from the FHIR server "
        "and tabulation."
    )
    fhir_url: Optional[str] = Field(
        description="The URL of the FHIR server from which data should be extracted, "
        "should end with '/fhir'. If not provided here then it must be set as an "
        "environment variable."
    )
    cred_manager: Optional[Literal["azure", "gcp"]] = Field(
        description="Chose a PHDI credential manager to use for authentication with the"
        " FHIR. May be set here or as an environment variable. If not provided anywhere"
        " then un-authenticated FHIR server requests will be attempted."
    )

    _check_schema_validity = validator("schema_", allow_reuse=True)(
        check_schema_validity
    )


@app.get("/")
async def health_check():
    """
    Check service status. If an HTTP 200 status code is returned along with
    '{"status": "OK"}' then the tabulation service is available and running properly.
    """
    return {"status": "OK"}


@app.post("/validate-schema", status_code=200)
async def validate_schema_endpoint(input: SchemaValidationInput):
    try:
        validate_schema(input.table_schema)
        return {"success": True, "isValid": True, "message": "Valid Schema"}
    except jsonschema.exceptions.ValidationError as e:
        print("Error: ", e)
        return {
            "success": True,
            "isValid": False,
            "message": "Invalid schema: Validation exception",
        }
    except jsonschema.exceptions.SchemaError as e:
        print("Error: ", e)
        return {
            "success": True,
            "isValid": False,
            "message": "Invalid schema: Schema error",
        }


@app.post("/tabulate", status_code=200)
async def tabulate_endpoint(input: TabulateInput, response: Response):
    """
    This endpoint will extract, tabulate, and persist data from a FHIR server according
    to a user-defined schema in the method of the user's choosing.
    """

    # Look for values that must be provided in the request body, or set as environment
    # variables.
    input = dict(input)
    required_values = ["fhir_url"]
    search_result = search_for_required_values(input, required_values)
    if search_result != "All values were found.":
        response.status_code = status.HTTP_400_BAD_REQUEST
        return search_result

    # Extract schema name from schema metadata.
    input["schema_name"] = input["schema_"]["metadata"].get("schema_name")

    # Instantiate a credential manager.
    if input["cred_manager"] is not None:
        input["cred_manager"] = get_cred_manager(
            cred_manager=input["cred_manager"], location_url=input["fhir_url"]
        )

    return tabulate(**input)


def tabulate(
    schema_: dict,
    output_type: Literal["parquet", "csv", "sql"],
    schema_name: Optional[str],
    fhir_url: str,
    cred_manager: BaseCredentialManager = None,
) -> dict:
    """
    Given a schema and FHIR server, extract the required data from the FHIR server,
    tabulate the data according to the schema, and persist the data according to the
    file type specified by output_type.

    :param schema_: A declarative, user-defined specification, for one or more tables,
        that defines the metadata, properties, and columns of those tables as they
        relate to FHIR resources. Additional information about creating and using these
        schema can be found at
        https://github.com/CDCgov/phdi/blob/main/tutorials/tabulation-tutorial.md.
    :output_type: Specifies how the data should be persisted after it has been extracted
        from a FHIR server and tabulated.
    :schema_name: The name for the schema.
    :fhir_url: The URL of the FHIR server data should be extracted from.
    :cred_manager: A credential manager that can be used handle authentication with FHIR
        server.
    """
    # Load search_urls to query FHIR server
    search_urls = _generate_search_urls(schema=schema_)
    directory = (
        Path()
        / "tables"
        / schema_name
        / datetime.datetime.now().strftime("%m-%d-%YT%H%M%S")
    )

    directory.mkdir(parents=True)
    for table_name, search_url in search_urls.items():
        next = search_url
        pq_writer = None
        while next is not None:
            # Return set of incremental results and next URL to query
            incremental_results, next = extract_data_from_fhir_search_incremental(
                search_url=urllib.parse.urljoin(fhir_url, next),
                cred_manager=cred_manager,
            )
            # Tabulate data for set of incremental results
            tabulated_incremental_data = tabulate_data(
                incremental_results, schema_, table_name
            )
            # Write set of tabulated incremental data
            pq_writer = write_data(
                tabulated_data=tabulated_incremental_data,
                directory=str(directory),
                filename=table_name,
                output_type=output_type,
                db_file=schema_name,
                db_tablename=table_name,
                pq_writer=pq_writer,
            )

        if pq_writer is not None:
            pq_writer.close()

    result = {
        "schema_name": schema_name,
        "output_type": output_type,
        "fhir_url": fhir_url,
        "tables": list(search_urls.keys()),
        "directory": str(directory),
    }
    return result
