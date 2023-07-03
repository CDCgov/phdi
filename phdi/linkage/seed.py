# This script converts patient data from parquet to patient FHIR resources.
from typing import Dict, Tuple
import uuid


def convert_to_patient_fhir_resources(data: Dict) -> Tuple:
    """
    Converts and returns a row of patient data into patient resource in a FHIR bundle
    with a newly generated id as well as the `iris_id`.

    :param data: Dictionary of patient data that optionionally includes the following
      fields: mrn, ssn, first_name, middle_name, last_name, home_phone, cell-phone, sex,
      birthdate, address, city, state, zip.
    :return: Tuple of the `iris_id` and FHIR bundle.
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
                "value": f"{data.get('mrn',None)}",
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
                "value": f"{data.get('ssn',None)}",
            },
        ],
        "name": [
            {
                "family": f"{data.get('last_name',None)}",
                "given": data.get("first_name", None).split()
                + data.get("middle_name", None).split(),
            }
        ],
        "telecom": [
            {
                "system": "phone",
                "value": f"{data.get('home_phone',None)}",
                "use": "home",
            },
            {
                "system": "phone",
                "value": f"{data.get('cell_phone',None)}",
                "use": "mobile",
            },
        ],
        "gender": f"{data.get('sex',None)}",
        "birthDate": f"{data.get('birthdate',None)}",
        "address": [
            {
                "use": "home",
                "line": [f"{data.get('address',None)}"],
                "city": f"{data.get('city',None)}",
                "state": f"{data.get('state',None)}",
                "postalCode": f"{data.get('zip',None)}",
            }
        ],
    }

    fhir_bundle = {
        "resourceType": "Bundle",
        "id": str(uuid.uuid4()),
        "entry": [{"fullUrl": f"urn:uuid:{patient_id}", "resource": patient_resource}],
    }

    return (data["iris_id"], fhir_bundle)
