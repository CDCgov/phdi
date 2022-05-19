import json
import pathlib
import copy

from phdi_building_blocks.standardize import (
    standardize_name,
    standardize_patient_name,
    standardize_phone,
    standardize_patient_phone,
)


def test_standardize_name():
    assert "JOHN DOE" == standardize_name(" JOHN DOE ")
    assert "JOHN DOE" == standardize_name(" John Doe3 ")


def test_standardize_patient_name():
    raw_bundle = json.load(
        open(pathlib.Path(__file__).parent / "assets" / "patient_bundle.json")
    )
    standardized_bundle = copy.deepcopy(raw_bundle)
    patient = standardized_bundle["entry"][1]["resource"]
    patient["name"][0]["family"] = "DOE"
    patient["name"][0]["given"] = ["JOHN", "DANGER"]
    patient["extension"] = []
    patient["extension"].append(
        {
            "url": "http://usds.gov/fhir/phdi/StructureDefinition/family-name-was-standardized",  # noqa
            "valueBoolean": True,
        }
    )
    patient["extension"].append(
        {
            "url": "http://usds.gov/fhir/phdi/StructureDefinition/given-name-was-standardized",  # noqa
            "valueBoolean": True,
        }
    )
    assert standardize_patient_name(raw_bundle) == standardized_bundle


def test_standardize_phone():
    assert "0123456789" == standardize_phone("0123456789")
    assert "0123456789" == standardize_phone("(012)345-6789")
    assert standardize_phone("345-6789") is None


def test_standardize_patient_phone():
    raw_bundle = json.load(
        open(pathlib.Path(__file__).parent / "assets" / "patient_bundle.json")
    )
    standardized_bundle = copy.deepcopy(raw_bundle.copy())
    patient = standardized_bundle["entry"][1]["resource"]
    patient["telecom"][0]["value"] = "1234567890"
    patient["extension"] = []
    patient["extension"].append(
        {
            "url": "http://usds.gov/fhir/phdi/StructureDefinition/phone-was-standardized",  # noqa
            "valueBoolean": True,
        }
    )
    assert standardize_patient_phone(raw_bundle) == standardized_bundle
