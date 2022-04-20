from typing import List
from GenerateCSVs.patient import PATIENT_COLUMNS, parse_patient_resource

ELR_SPECIFIC_COLUMNS = ["loincCode", "result", "effectiveDateTime"]

ELR_COLUMNS = PATIENT_COLUMNS + ELR_SPECIFIC_COLUMNS


def extract_loinc_lab(observation: dict) -> List[str]:
    """
    Given an observation FHIR profile, determine whether the profile
    contains information related to a laboratory test and result.
    If yes, collect the relevant lab code, test result, and test
    date into a list.
    """
    code = observation["code"]["coding"][0]
    if "loinc" in code["system"] and "valueCodeableConcept" in observation:
        obs_date = observation["effectiveDateTime"]
        result = observation["valueCodeableConcept"]["coding"][0]["display"]
        return [code["code"], result, obs_date]
    return []


def elr_to_csv(bundle: dict) -> List[List[str]]:
    """
    Given a FHIR bundle containing a patient resource and one or more
    ELR lab observations, identify the labs related to COVID and turn
    them into patient-identified rows for use in a CSV.
    """
    rows_to_write = []
    patient_info_list = []
    for resource in bundle["entry"]:
        if resource["resource"]["resourceType"] == "Patient":
            patient_info_list.extend(parse_patient_resource(resource))
        elif resource["resource"]["resourceType"] == "Observation":

            # We only care about observations related to covid testing
            obs_info = extract_loinc_lab(resource["resource"])
            if len(obs_info) > 0:
                rows_to_write.append(obs_info)

    # Now pre-pend the patient information to each row
    # Handles case where Patient resource comes after 1+ obs profiles
    for i in range(len(rows_to_write)):
        rows_to_write[i] = patient_info_list + rows_to_write[i]
    return rows_to_write
