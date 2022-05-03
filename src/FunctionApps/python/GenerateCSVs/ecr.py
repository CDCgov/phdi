import logging

from typing import List
from GenerateCSVs.patient import PATIENT_COLUMNS, parse_patient_resource
from GenerateCSVs.elr import ELR_SPECIFIC_COLUMNS, extract_loinc_lab
from GenerateCSVs.vxu import VXU_SPECIFIC_COLUMNS, parse_immunization_resource

ECR_COLUMNS = (
    PATIENT_COLUMNS
    + [
        f"immunization{column[0].upper() + column[1:]}"
        for column in VXU_SPECIFIC_COLUMNS
    ]
    + [
        f"observation{column[0].upper() + column[1:]}"
        for column in ELR_SPECIFIC_COLUMNS
    ]
)


def ecr_to_csv(bundle: dict) -> List[List[str]]:
    """
    Given a FHIR bundle containing a patient resource and one or more
    immunization resources, create a row containing data specified by
    ECR_COLUMNS.
    """
    # Initialize variables
    patient_resources = {}
    entries = []
    return_rows = []

    # Loop through bundle, and build:
    #  * A dictionary to index patient resources
    #  * A list of immunization records that should appear in the CSV
    #  * A list of observation records that should appear in the CSV
    for entry in bundle.get("entry"):
        resource = entry["resource"]
        if resource.get("resourceType") == "Patient" and len(resource.get("id")) > 0:
            patient_resources["Patient/" + resource.get("id")] = parse_patient_resource(
                entry
            )
        elif resource.get("resourceType") in ["Immunization", "Observation"]:
            entries.append(entry)

    # Loop through immunization resources collected from bundle.
    # For each immunization resource, pull in its corresponding patient
    # and join immunization-specific fields.
    for entry in entries:
        resource = entry["resource"]
        resource_type = resource["resourceType"]
        resource_id = resource.get("id")
        # Pull out patient reference from immunization record
        pat_ref = ""
        if (
            resource_type == "Immunization"
            and type(resource.get("patient")) == dict
            and type(resource.get("patient").get("reference")) == str
        ):
            pat_ref = resource.get("patient").get("reference")
        elif (
            resource_type == "Observation"
            and type(resource.get("subject")) == dict
            and type(resource.get("subject").get("reference")) == str
        ):
            pat_ref = resource.get("subject").get("reference")

        # Make sure patient reference exists, and is found in patient_resources
        # Build a row in the CSV.
        try:
            if pat_ref and patient_resources.get(pat_ref):
                if resource_type == "Immunization":
                    imm_values = parse_immunization_resource(resource)

                    # Need a vaccine code or description to create a row.
                    if imm_values[0:2] != ["", ""]:
                        return_rows.append(
                            patient_resources.get(pat_ref) + imm_values + ["", "", ""]
                        )
                elif resource_type == "Observation":
                    obs_values = extract_loinc_lab(resource)

                    # extract_loinc_lab will return an empty array
                    # if it fails to find enough info in the provided array.
                    if len(obs_values) > 0:
                        return_rows.append(
                            patient_resources.get(pat_ref) + ["", "", ""] + obs_values
                        )
        except Exception as err:
            logging.warning(
                f"Parsing failed due to {type(err)} error in resource {resource_id} of "
                + f"type {resource_type}: {err}"
            )

    return return_rows
