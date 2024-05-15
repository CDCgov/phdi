from pathlib import Path

from dibbs.base_service import BaseService
from fastapi import Response

from app.models import InsertConditionInput
from app.utils import get_clean_snomed_code
from app.utils import get_clinical_services_dict
from app.utils import get_clinical_services_list

# Instantiate FastAPI via DIBBs' BaseService class
app = BaseService(
    service_name="Trigger Code Reference",
    service_path="/trigger-code-reference",
    description_path=Path(__file__).parent.parent / "description.md",
).start()


@app.get("/")
async def health_check():
    """
    Check service status. If an HTTP 200 status code is returned along with
    '{"status": "OK"}' then the reference service is available and running
    properly.
    """
    return {"status": "OK"}


@app.post("/insert-condition-extensions/")
async def insert_condition_extensions(input: InsertConditionInput) -> Response:
    """
    Extends the resources of a supplied FHIR bundle with extension tags
    related to one or more supplied conditions. For each condition in the
    given list of conditions, each resource in the bundle is appended with
    an extension structure indicating which SNOMED condition code the
    resource is linked to.

    :param input: A request formatted as an InsertConditionInput, containing a
      FHIR bundle whose resources to extend and one or more SNOMED condition
      code strings to extend by.
    :return: HTTP Response containing the bundle with resources extended by
      any linked conditions.
    """
    # TODO: This method is a stub.
    return {"extended_bundle": input.bundle}


@app.get("/get-value-sets/")
async def get_value_sets_for_condition(condition_code: str) -> Response:
    """
    For a given condition, queries and returns the value set of clinical
    services associated with that condition.

    :param condition_code: A query param supplied as a string representing a
      single SNOMED condition code.
    :return: An HTTP Response containing the value sets of the queried code.
    """
    if condition_code is None or condition_code == "":
        return Response(
            content="Supplied condition code must be a non-empty string",
            status_code=422,
        )
    else:
        clean_snomed_code = get_clean_snomed_code(condition_code)
        clinical_services_list = get_clinical_services_list(clean_snomed_code)
        values = get_clinical_services_dict(
            clinical_services_list, filter_clinical_services=None
        )
    return {"value_set": values}
