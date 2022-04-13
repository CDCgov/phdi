import json
import pathlib
from GenerateCSVs.patient import parse_patient_resource


def test_parse_patient_resource():

    patient = json.load(
        open(pathlib.Path(__file__).parent / "assets" / "patient_bundle.json")
    )

    patient_empty = json.load(
        open(pathlib.Path(__file__).parent / "assets" / "patient_bundle_empty.json")
    )

    assert parse_patient_resource(patient) == [
        "292561276fcdefab6a2a1545abf7aa9bf30906ba6f0d4f8faff652efc3b4ab3c",
        "JANE",
        "DOE",
        "1950-01-28",
        "female",
        "123 Main Street",
        "Gotham",
        "XY",
        "12345",
        "3.14159",
        "2.71828",
        "2054-5",
        "2186-5",
    ]
    assert parse_patient_resource(patient_empty) == [""] * 13
