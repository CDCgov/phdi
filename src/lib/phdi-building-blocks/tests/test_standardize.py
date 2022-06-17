import json
import pathlib
import copy


from phdi_building_blocks.standardize import (
    standardize_patient_names,
    standardize_all_phones,
    extract_countries_from_resource,
    standardize_country,
)

# TODO: Implement missing unit test for standardize.standardize_phone()


def test_standardize_patient_name():
    raw_bundle = json.load(
        open(pathlib.Path(__file__).parent / "assets" / "patient_bundle.json")
    )
    standardized_bundle = copy.deepcopy(raw_bundle)
    patient = standardized_bundle["entry"][1]["resource"]
    patient["name"][0]["family"] = "DOE"
    patient["name"][0]["given"] = ["JOHN", "DANGER"]
    assert standardize_patient_names(raw_bundle) == standardized_bundle


def test_extract_countries_from_resource():
    raw_bundle = json.load(
        open(pathlib.Path(__file__).parent / "assets" / "patient_bundle.json")
    )
    patient = raw_bundle["entry"][1].get("resource")
    patient["address"].append(patient["address"][0])
    patient["address"].append(patient["address"][0])
    patient_resource = raw_bundle["entry"][1]
    assert [
        country for country in extract_countries_from_resource(patient_resource)
    ] == ["US"] * 3
    assert [
        country
        for country in extract_countries_from_resource(patient_resource, "alpha_3")
    ] == ["USA"] * 3
    assert [
        country
        for country in extract_countries_from_resource(patient_resource, "numeric")
    ] == ["840"] * 3


def test_standardize_country():
    assert standardize_country("US") == "US"
    assert standardize_country("USA") == "US"
    assert standardize_country("United States of America") == "US"
    assert standardize_country("United states ") == "US"
    assert standardize_country("US", "alpha_3") == "USA"
    assert standardize_country("USA", "numeric") == "840"


def test_standardize_patient_phone():
    raw_bundle = json.load(
        open(pathlib.Path(__file__).parent / "assets" / "patient_bundle.json")
    )
    standardized_bundle = copy.deepcopy(raw_bundle.copy())
    patient = standardized_bundle["entry"][1]["resource"]
    patient["telecom"][0]["value"] = "+11234567890"
    assert standardize_all_phones(raw_bundle) == standardized_bundle
