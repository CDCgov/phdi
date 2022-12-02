from fastapi import FastAPI, Response
from pydantic import BaseModel


app = FastAPI()


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
