from fastapi import FastAPI, Response
from pydantic import BaseModel, validator
from typing import Optional, Literal
import urllib.parse
from phdi.cloud.core import BaseCredentialManager
from phdi.tabulation.tables import validate_schema, write_data
from phdi.fhir.tabulation.tables import _generate_search_urls, extract_data_from_fhir_search_incremental, tabulate_data

api = FastAPI()


class TabulateInput(BaseModel):
    """
    Request schema for the tabulate endpoint.
    """

    schema: dict
    output_type: Literal["parquet", "csv", "sql"]
    schema_name: Optional[str]
    fhir_url: Optional[str]
    cred_manager: Optional[Literal["azure","gcp"]]

    _check_schema_validity = validator("schema", allow_reuse=True)(
    validate_schema
)


@api.get("/")
async def health_check():
    return {"status": "OK"}


@api.post("/tabulate", status_code=200)
async def convert(input: TabulateInput, response: Response):

    return tabulate(**dict(input))


def tabulate(
    schema: dict,
    fhir_url: str,
    cred_manager: BaseCredentialManager, 
) -> dict:
    """
    Tabulate the given schema.

    :param schema: The schema to tabulate.
    """
    # Load search_urls to query FHIR server
    search_urls = _generate_search_urls(schema=schema)

    for table_name, search_url in search_urls.items():
        next = search_url
        while next is not None:

            # Return set of incremental results and next URL to query
            incremental_results, next = extract_data_from_fhir_search_incremental(
                search_url=urllib.parse.urljoin(fhir_url, search_url),
                cred_manager=cred_manager,
            )
            # Tabulate data for set of incremental results
            tabulated_incremental_data = tabulate_data(
                incremental_results, schema, table_name
            )

            # Write set of tabulated incremental data
            write_data(
                tabulated_data=tabulated_incremental_data,
                directory=output_params[table_name].get("directory"),
                filename=output_params[table_name].get("filename"),
                output_type=output_params[table_name].get("output_type"),
                db_file=output_params[table_name].get("db_file", None),
                db_tablename=output_params[table_name].get("db_filename", None),
                pq_writer=output_params[table_name].get("pq_writer", None),
            )
    return {}
