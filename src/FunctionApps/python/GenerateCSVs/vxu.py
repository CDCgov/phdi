from typing import List
from GenerateCSVs.patient import PATIENT_COLUMNS
from GenerateCSVs.patient import parse_patient_resource

VXU_COLUMNS = PATIENT_COLUMNS + [
    "vaccineCode",
    "vaccineDescription",
    "occurrenceDateTime",
]


def vxu_to_csv(bundle: dict) -> List[List[str]]:
    """
    Given a FHIR bundle containing a patient resource and one or more
    immunization resources, create a row containing data specified by
    VXU_COLUMNS.
    """
    # Initialize variables
    patient_resources = {}
    immunization_resources = []
    return_rows = []

    # Loop through bundle, and build:
    #  * A dictionary to index patient resources
    #  * A list of immunization records that should appear in the CSV
    for entry in bundle.get("entry"):
        resource = entry["resource"]
        if resource.get("resourceType") == "Patient" and len(resource.get("id")) > 0:
            patient_resources["Patient/" + resource.get("id")] = parse_patient_resource(
                entry
            )
        elif resource.get("resourceType") == "Immunization":
            immunization_resources.append(resource)

    # Loop through immunization resources collected from bundle.
    # For each immunization resource, pull in its corresponding patient
    # and join immunization-specific fields.
    for imm_rsc in immunization_resources:

        # Pull out patient reference from immunization record
        pat_ref = ""
        if (
            type(imm_rsc.get("patient")) == dict
            and type(imm_rsc.get("patient").get("reference")) == str
        ):
            pat_ref = imm_rsc.get("patient").get("reference")

        # Make sure patient reference exists, and is found in patient_resources
        # If so, build a row in the CSV.
        if pat_ref and patient_resources.get(pat_ref):
            return_rows.append(
                patient_resources.get(pat_ref) + parse_immunization_resource(imm_rsc)
            )

    return return_rows


def parse_immunization_resource(imm_rsc: dict) -> List[str]:
    """Extract data from an immunization resource"""
    return get_vax_code_desc(imm_rsc) + get_vax_datetime(imm_rsc)


def get_vax_code_desc(imm_rsc) -> List[str]:
    """Extract vaccine code and description from an immunization resource"""
    if (
        imm_rsc.get("vaccineCode") is None
        or imm_rsc.get("vaccineCode").get("coding") is None
    ):
        return [""]

    for code in imm_rsc.get("vaccineCode").get("coding"):
        if code.get("code") is not None and code.get("system") is not None:
            # This is maybe a little more permissive than it should be.
            # Technically `system` should be http://hl7.org/fhir/sid/cvx
            # But our data has the following
            # http://example.com/v2-to-fhir-converter/CodeSystem/CVX
            # If this is fixed in upstream translation, we could make this stricter.
            if code.get("system").lower().endswith("cvx"):
                return [code.get("code", ""), code.get("display", "")]


def get_vax_datetime(imm_rsc) -> List[str]:
    """Extract vaccination date/time from an immunization resource"""
    return [imm_rsc.get("occurrenceDateTime", "")]
