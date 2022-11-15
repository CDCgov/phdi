from fastapi import FastAPI, Response
from pydantic import BaseModel


api = FastAPI()


class TabulationInput(BaseModel):
    """
    Input parameters for the tabulation service.
    """

    table_schema: dict


@api.get("/")
async def health_check():
    return {"status": "OK"}


@api.post("/tabulate", status_code=200)
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
