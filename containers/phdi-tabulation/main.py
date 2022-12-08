from fastapi import FastAPI, Response
from pydantic import BaseModel
from pathlib import Path


description = Path('description.md').read_text()
app = FastAPI(
    title="PHDI Ingestion Service",
    description=description,
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
)


class TabulationInput(BaseModel):
    """
    Input parameters for the tabulation service.
    """

    table_schema: dict


@app.get("/")
async def health_check():
    return {"status": "OK"}


@app.post("/tabulate", status_code=200)
async def convert(input: TabulationInput, response: Response):

    return tabulate(**dict(input))


def tabulate(
    table_schema: dict,
) -> dict:
    """
    Tabulate the given schema.

    :param schema: The schema to tabulate.
    """

    return {}
