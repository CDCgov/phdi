import json
import pathlib
import copy

from phdi.fhir.harmonization.standardization import (
    _standardize_names_in_resource,
    _standardize_phones_in_resource,
    _extract_countries_from_resource,
)


def test_standardize_names_in_resource():
    raw_bundle = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "patient_bundle.json"
        )
    )
    patient_resource = raw_bundle["entry"][1]["resource"]
    standardized_patient = copy.deepcopy(patient_resource)
    standardized_patient["name"][0]["family"] = "DOE"
    standardized_patient["name"][0]["given"] = ["JOHN", "DANGER"]
    assert _standardize_names_in_resource(patient_resource) == standardized_patient


def test_standardize_phones_in_resource():
    raw_bundle = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "patient_bundle.json"
        )
    )
    patient_resource = raw_bundle["entry"][1]["resource"]
    standardized_patient = copy.deepcopy(patient_resource)
    standardized_patient["telecom"][0]["value"] = "+11234567890"
    assert _standardize_phones_in_resource(patient_resource) == standardized_patient


def test_extract_countries_from_resource():
    raw_bundle = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "patient_bundle.json"
        )
    )
    patient = raw_bundle["entry"][1].get("resource")
    patient["address"].append(patient["address"][0])
    patient["address"].append(patient["address"][0])
    assert [country for country in _extract_countries_from_resource(patient)] == [
        "US"
    ] * 3
    assert [
        country for country in _extract_countries_from_resource(patient, "alpha_3")
    ] == ["USA"] * 3
    assert [
        country for country in _extract_countries_from_resource(patient, "numeric")
    ] == ["840"] * 3
