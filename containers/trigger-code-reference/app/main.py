from pathlib import Path
from typing import Annotated

from dibbs.base_service import BaseService
from fastapi import Body
from fastapi import Response

from app.models import InsertConditionInput
from app.utils import _find_codes_by_resource_type
from app.utils import _stamp_resource_with_code_extension
from app.utils import get_clean_snomed_code
from app.utils import get_clinical_services_dict
from app.utils import get_clinical_services_list
from app.utils import read_json_from_assets

RESOURCE_TO_SERVICE_TYPES = {
    "Observation": ["dxtc", "ostc", "lotc", "lrtc", "mrtc", "sdtc"],
    "Condition": ["dxtc", "sdtc"],
    "Immunization": ["ostc", "lotc", "lrtc"],
    "DiagnosticReport": ["dxtc", "ostc", "lotc", "lrtc", "mrtc", "sdtc"],
}

# Instantiate FastAPI via DIBBs' BaseService class
app = BaseService(
    service_name="Trigger Code Reference",
    service_path="/trigger-code-reference",
    description_path=Path(__file__).parent.parent / "description.md",
).start()

# Load up the annotated examples
stamp_conditions_request_examples = read_json_from_assets(
    "sample_stamp_condition_extensions_requests.json"
)
stamp_conditions_response_examples_raw = read_json_from_assets(
    "sample_stamp_condition_extensions_responses.json"
)
stamp_conditions_response_examples = {200: stamp_conditions_response_examples_raw}


@app.get("/")
async def health_check():
    """
    Check service status. If an HTTP 200 status code is returned along with
    '{"status": "OK"}' then the reference service is available and running
    properly.
    """
    return {"status": "OK"}


@app.post(
    "/stamp-condition-extensions",
    status_code=200,
    responses=stamp_conditions_response_examples,
)
async def stamp_condition_extensions(
    input: Annotated[
        InsertConditionInput, Body(examples=stamp_conditions_request_examples)
    ],
) -> Response:
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
    # Collate all clinical services for each of the supplied conditions to
    # extend, collected by service type
    stamp_codes_to_service_codes = {}
    for cond in input.conditions:
        cond_list = get_clinical_services_list([cond])
        cond_dict = get_clinical_services_dict(cond_list)
        stamp_codes_to_service_codes[cond] = cond_dict

    bundle_entries = input.bundle.get("entry", [])
    for entry in bundle_entries:
        resource = entry.get("resource", {})
        rtype = resource.get("resourceType")
        if rtype in RESOURCE_TO_SERVICE_TYPES:
            # Some resources might be coded in one or more schemes, so we'll
            # need to check for any that are applicable
            r_codes = _find_codes_by_resource_type(resource)
            if len(r_codes) == 0:
                continue

            # Want to check each queried condition for extension codes
            for cond in input.conditions:
                # Only need a single instance of service type lookup to contain
                # the resource's code
                should_stamp = False
                stamp_checks = stamp_codes_to_service_codes[cond]

                # Use only the service types allowed by the current
                # resource
                for stype in RESOURCE_TO_SERVICE_TYPES[rtype]:
                    if stype in stamp_checks:
                        for code_sys_obj in stamp_checks[stype]:
                            for rcode in r_codes:
                                if rcode in code_sys_obj["codes"]:
                                    should_stamp = True
                                    break
                            if should_stamp:
                                break
                    if should_stamp:
                        break

                if should_stamp:
                    entry["resource"] = _stamp_resource_with_code_extension(
                        resource, cond
                    )

    return {"extended_bundle": input.bundle}


@app.get("/get-value-sets/")
async def get_value_sets_for_condition(
    condition_code: str, filter_clinical_services: list = None
) -> Response:
    """
    For a given condition, queries and returns the value set of clinical
    services associated with that condition.

    :param condition_code: A query param supplied as a string representing a
      single SNOMED condition code.
    :param filter_clinical_services: (Optional) List of clinical service types
      specified to keep. By default, all (currently) 6 clinical service types are
      returned; use this parameter to return only types of interest.
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
            clinical_services_list, filter_clinical_services
        )
    return values
