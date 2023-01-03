from fastapi import FastAPI, Response
from pydantic import BaseModel, Field
import jsonschema

from phdi.tabulation import validate_schema

api = FastAPI()


class TabulationInput(BaseModel):
    """
    Input parameters for the tabulation service.
    """

    table_schema: dict = Field(
        alias="schema", description="A JSON formatted PHDI schema."
    )


@api.get("/")
async def health_check():
    return {"status": "OK"}


@api.post("/validate-schema", status_code=200)
async def validate_schema_endpoint(input: TabulationInput, response: Response):
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
