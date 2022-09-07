import json
import pathlib

from phdi.fhir.utils import (
    find_entry_by_resource_type,
    get_field,
)


def test_find_resource_by_type():
    bundle = json.load(
        open(pathlib.Path(__file__).parent.parent / "assets" / "patient_bundle.json")
    )
    found_patients = find_entry_by_resource_type(bundle, "Patient")
    assert len(found_patients) == 1
    assert found_patients[0].get("resource").get("resourceType") == "Patient"


def test_get_field():
    bundle = json.load(
        open(pathlib.Path(__file__).parent.parent / "assets" / "patient_bundle.json")
    )
    patient = bundle["entry"][1]["resource"]
    assert get_field(patient, "telecom", "home", 0) == {
        "use": "home",
        "system": "phone",
        "value": "123-456-7890",
    }
    assert get_field(patient, "telecom", "mobile", 1) == {
        "value": "johndanger@doe.net",
        "system": "email",
    }
