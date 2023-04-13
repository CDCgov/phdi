from phdi.linkage.seed import (
    convert_to_patient_fhir_resources,
    _insert_patient_resource_id,
)
import pathlib


mpi_test_file_path = (
    pathlib.Path(__file__).parent.parent.parent
    / "tests"
    / "assets"
    / "synthetic_patient_mpi_seed_data.gzip"
)


def test_insert_patient_resource_id():
    test_data = {
        "iris_id": "264a0878-bb2b-350e-845c-5f694b261495",
        "birthdate": "1967-04-17",
        "ssn": "123-456-7890",
        "mrn": "999-15-2572",
        "first_name": "Marlin",
        "middle_name": "Middle",
        "last_name": "Stehr",
        "sex": "male",
        "address": "522 Ratke Burg",
        "city": "Los Angeles",
        "state": "California",
        "zip": 91607.0,
        "email": "HgidjtzaZK@hotmail.com",
        "home_phone": 3103115637,
        "cell_phone": 6613277108,
    }

    test_patient_resource = {
        "resourceType": "Patient",
        "id": "",
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
                "value": "999-15-2572",
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
                "value": "123-456-7890",
            },
        ],
        "name": {"family": "Stehr", "given": ["Marlin", "Middle"]},
        "telecom": [
            {"system": "phone", "value": "3103115637", "use": "home"},
            {"system": "phone", "value": "6613277108", "use": "mobile"},
        ],
        "gender": "male",
        "birthDate": "1967-04-17",
        "address": [
            {
                "use": "home",
                "line": ["522 Ratke Burg"],
                "city": "Los Angeles",
                "state": "California",
                "postalCode": "91607.0",
            }
        ],
    }

    expected_patient_id = (
        "812acdd0b6833671f89e3d655cca2288140edfff75b7d6376bafc93c206104d2"
    )
    returned_patient_resource = _insert_patient_resource_id(
        data=test_data, patient_resource=test_patient_resource
    )
    assert expected_patient_id == returned_patient_resource["id"]

    # Test that hashed id does not match when info is changed
    test_data["sex"] = "female"
    returned_patient_resource = _insert_patient_resource_id(
        data=test_data, patient_resource=test_patient_resource
    )
    assert expected_patient_id != returned_patient_resource["id"]


def test_convert_to_patient_fhir_resources():
    returned_fhir_resources = convert_to_patient_fhir_resources(mpi_test_file_path)
    assert type(returned_fhir_resources) == list
    assert type(returned_fhir_resources[0]) == dict
    assert returned_fhir_resources[0]["resourceType"] == "Patient"
    assert returned_fhir_resources[0]["id"] != ""
