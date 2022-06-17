from phdi_building_blocks.utils import (
    find_resource_by_type,
    get_one_line_address,
    get_field,
    standardize_text,
)
import pathlib
import json


def test_find_resource_by_type():
    bundle = json.load(
        open(pathlib.Path(__file__).parent / "assets" / "patient_bundle.json")
    )
    found_patients = find_resource_by_type(bundle, "Patient")
    assert len(found_patients) == 1
    assert found_patients[0].get("resource").get("resourceType") == "Patient"


def test_get_one_line_address():
    bundle = json.load(
        open(pathlib.Path(__file__).parent / "assets" / "patient_bundle.json")
    )
    patient = bundle["entry"][1]["resource"]
    result_address = "123 Fake St Unit #F Faketon, NY 10001-0001"
    assert get_one_line_address(patient.get("address", [])[0]) == result_address


def test_get_field():
    bundle = json.load(
        open(pathlib.Path(__file__).parent / "assets" / "patient_bundle.json")
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


def test_standardize_text():
    raw_text = " 12 PhDi is ReaLLy KEWL !@#$ 34"
    set_1 = {"case": "lower", "trim": True}
    answer_1 = "12 phdi is really kewl !@#$ 34"
    set_2 = {"remove_numbers": True, "trim": True}
    answer_2 = "PhDi is ReaLLy KEWL !@#$"
    set_3 = {
        "remove_punctuation": True,
        "remove_characters": ["R", "a", "l", "L", "y", "K"],
    }
    answer_3 = " 12 PhDi is e EW  34"
    assert standardize_text(raw_text, **set_1) == answer_1
    assert standardize_text(raw_text, **set_2) == answer_2
    assert standardize_text(raw_text, **set_3) == answer_3
