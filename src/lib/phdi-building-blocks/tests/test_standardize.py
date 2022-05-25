import json
import pathlib
import copy


from phdi_building_blocks.standardize import (
    standardize_name,
    standardize_patient_name,
    standardize_phone,
    country_extractor,
    standardize_country,
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
    raw_bundle = json.load(
        open(pathlib.Path(__file__).parent / "assets" / "patient_bundle.json")
    )
    patient = raw_bundle["entry"][1]
    countries = country_extractor(patient)

    assert standardize_phone("+11234567890") == "+11234567890"
    assert standardize_phone("(123)-456-7890", countries) == "+11234567890"
    assert standardize_phone("123 456.7890") == "+11234567890"


def test_country_extractor():
    raw_bundle = json.load(
        open(pathlib.Path(__file__).parent / "assets" / "patient_bundle.json")
    )
    patient = raw_bundle["entry"][1]
    patient["resource"]["address"].append(patient["resource"]["address"][0])
    patient["resource"]["address"].append(patient["resource"]["address"][0])
    assert [country for country in country_extractor(patient)] == ["US"] * 3
    assert [country for country in country_extractor(patient, "alpha_3")] == ["USA"] * 3
    assert [country for country in country_extractor(patient, "numeric")] == ["840"] * 3


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
    patient["extension"] = []
    patient["extension"].append(
        {
            "url": "http://usds.gov/fhir/phdi/StructureDefinition/phone-was-standardized",  # noqa
            "valueBoolean": True,
        }
    )
    assert standardize_patient_phone(raw_bundle) == standardized_bundle
