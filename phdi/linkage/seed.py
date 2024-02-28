# This script converts patient data from parquet to patient FHIR resources.
import uuid
from datetime import datetime
from typing import Dict
from typing import Tuple


def extract_given_name(data: Dict):
    first_name = data.get("first_name", None)
    middle_name = data.get("middle_name", None)

    given_names = []

    for name in [first_name, middle_name]:
        if name is not None:
            for n in name.split():
                given_names.append(n)

    if len(given_names) > 0:
        return given_names
    else:
        return None


def adjust_birthdate(data: Dict):
    # TODO: remove this function and pass in the `format` parameter to dob
    # standardization in ReadSourceData for LAC
    format = "%d%b%Y:00:00:00.000"
    dob = data.get("birthdate", None)
    if dob is not None and ":" in dob:
        datetime_str = datetime.strptime(dob, format)
        dob = datetime_str.strftime("%Y-%m-%d")
    return dob


def convert_to_patient_fhir_resources(data: Dict) -> Tuple:
    """
    Converts and returns a row of patient data into patient resource in a FHIR-formatted
    patient resouce with a newly generated patient id as well as the
    `external_person_id`.

    :param data: Dictionary of patient data that optionionally includes the following
      fields: mrn, ssn, first_name, middle_name, last_name, home_phone, cell-phone, sex,
      birthdate, address, city, state, zip.
    :return: Tuple of the `external_person_id` and FHIR-formatted patient resource.
    """

    patient_id = str(uuid.uuid4())

    # Iterate through each patient and convert patient data to FHIR resource
    patient_resource = {
        "resourceType": "Patient",
        "id": f"{patient_id}",
        "identifier": [
            {
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                            "code": "MR",
                        }
                    ]
                },
                "value": f"{data.get('mrn', None)}",
            },
            {
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                            "code": "SS",
                        }
                    ]
                },
                "value": f"{data.get('ssn', None)}",
            },
        ],
        "name": [
            {
                "family": f"{data.get('last_name', None)}",
                "given": extract_given_name(data),
            }
        ],
        "telecom": [
            {
                "system": "phone",
                "value": f"{data.get('home_phone', None)}",
                "use": "home",
            },
            {
                "system": "phone",
                "value": f"{data.get('cell_phone', None)}",
                "use": "mobile",
            },
            {"value": f"{data.get('email', None)}", "system": "email"},
        ],
        "gender": f"{data.get('sex', None)}",
        "birthDate": adjust_birthdate(data),
        "address": [
            {
                "use": "home",
                "line": [f"{data.get('address', None)}"],
                "city": f"{data.get('city', None)}",
                "state": f"{data.get('state', None)}",
                "postalCode": f"{data.get('zip', None)}",
            }
        ],
    }

    fhir_bundle = {
        "resourceType": "Bundle",
        "type": "batch",
        "id": str(uuid.uuid4()),
        "entry": [
            {
                "fullUrl": f"urn:uuid:{patient_id}",
                "resource": patient_resource,
                "request": {"method": "PUT", "url": f"Patient/{patient_id}"},
            },
        ],
    }

    external_person_id = data.get("person_id", None)
    return (external_person_id, fhir_bundle)
