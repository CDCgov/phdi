# This script converts patient data from parquet to patient FHIR resources.
import pyarrow.parquet as pq
import pathlib
from typing import List, Dict

from phdi.linkage.link import generate_hash_str


def convert_to_patient_fhir_resources(file_path: pathlib.Path = None) -> List:
    """
    Converts a parquet file of patient data into a list of FHIR patient resources.

    :param file_path: Pathlib to flat file containing patient data, defaults to None
    :return: List of FHIR patient resources
    """
    parquet_file = pq.ParquetFile(file_path)

    patient_resources = []
    # Iterate through each patient and convert patient data to FHIR resource
    for row in parquet_file.iter_batches(batch_size=1):
        data = row.to_pylist()[0]
        patient_resource = {
            "resourceType": "Patient",
            "id": None,
            "identifier": [
                {
                    "type": {
                        "coding": [
                            {
                                "system": """http://terminology.hl7.org
                                /CodeSystem/v2-0203""",
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
                                "system": """http://terminology.hl7.org
                                /CodeSystem/v2-0203""",
                                "code": "SS",
                            }
                        ]
                    },
                    "value": f"{data.get('ssn',None)}",
                },
            ],
            "name": {
                "family": f"{data.get('last_name',None)}",
                "given": data.get("first_name", None).split()
                + data.get("middle_name", None).split(),
            },
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
        patient_resource = _insert_patient_resource_id(data, patient_resource)
        patient_resources.append(patient_resource)

    return patient_resources


def _insert_patient_resource_id(data: Dict, patient_resource: Dict) -> Dict:
    """
    Generates an ID for the patient resource based on hashing linking identifiers (
      birthdate, first_name, middle_name, last_name, sex, and address) and inserts the
      generated ID into the patient resource

    :param data: Dictionary containing a single patient's data from the flat file.
    :param patient_resource: Dictionary containing a single patient's data from the
      flat file formatted as a patient FHIR resource.
    :return: Dictionary containing a single patient's data from the
      flat file formatted as a patient FHIR resource with an `id`.
    """
    linking_identifier = "".join(
        data[identifier]
        for identifier in [
            "birthdate",
            "first_name",
            "middle_name",
            "last_name",
            "sex",
            "address",
        ]
    )

    patient_resource_id = generate_hash_str(
        linking_identifier=linking_identifier, salt_str="mpi-salt"
    )

    patient_resource["id"] = patient_resource_id

    return patient_resource
