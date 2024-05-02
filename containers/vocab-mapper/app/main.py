from pathlib import Path

from dibbs.base_service import BaseService
from fastapi import Response

from app.models import InsertConditionInput
from app.models import ValueSetForConditionInput

# Instantiate FastAPI via DIBBs' BaseService class
app = BaseService(
    service_name="Vocabulary Mapper",
    service_path="/vocab-mapper",
    description_path=Path(__file__).parent.parent / "description.md",
).start()


@app.get("/")
async def health_check():
    """
    Check service status. If an HTTP 200 status code is returned along with
    '{"status": "OK"}' then the mapper service is available and running
    properly.
    """
    return {"status": "OK"}


@app.post("/ersd/insert-condition-extensions/")
async def insert_condition_extensions(input: InsertConditionInput, response: Response):
    """
    Extends the resources of a supplied FHIR bundle with extension tags
    related to one or more supplied conditions. For each condition in the
    given list of conditions, each resource in the bundle is appended with
    an extension structure indicating which snowmed condition code the
    resource is linked to.
    """
    # TODO: This method is a stub.
    return {"extended_bundle": input.bundle}


@app.post("/ersd/get-value-sets/")
async def get_value_sets_for_condition(
    input: ValueSetForConditionInput, response: Response
):
    """
    For a given condition, queries and returns the value set of clinical
    services associated with that condition.
    """
    # TODO: This method is a stub.
    return {"value_set": []}
