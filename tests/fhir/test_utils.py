import json
import pathlib

from phdi.fhir.utils import (
    find_entries_by_resource_type,
    get_field,
    get_one_line_address,
)


def test_find_resource_by_type():

    # Empty dictionary case, with no key for entries
    bundle = {}
    found_patients = find_entries_by_resource_type(bundle, "Patient")
    assert len(found_patients) == 0

    # Case where entry exists but is an empty list
    bundle = {"entry": []}
    found_patients = find_entries_by_resource_type(bundle, "Patient")
    assert len(found_patients) == 0

    # Regular use case: entry exists and has resources of given type
    bundle = json.load(
        open(pathlib.Path(__file__).parent.parent / "assets" / "patient_bundle.json")
    )
    found_patients = find_entries_by_resource_type(bundle, "Patient")
    assert len(found_patients) == 1
    assert found_patients[0].get("resource").get("resourceType") == "Patient"


def test_get_field():
    bundle = json.load(
        open(pathlib.Path(__file__).parent.parent / "assets" / "patient_bundle.json")
    )
    patient = bundle["entry"][1]["resource"]

    # Success cases of finding field
    assert get_field(patient, "telecom", "home") == {
        "use": "home",
        "system": "phone",
        "value": "123-456-7890",
    }
    assert get_field(patient, "telecom", "mobile", 1) == {
        "value": "johndanger@doe.net",
        "system": "email",
    }

    # Failure cases: undefined and mismatched inputs inputs
    try:
        get_field(patient, "", "home")
    except Exception as e:
        assert repr(e) == "ValueError('Field must be a defined, non-empty string')"

    try:
        get_field(patient, "telecom", "")
    except Exception as e:
        assert repr(e) == "ValueError('Use must be a defined, non-empty string')"

    try:
        get_field({}, "telecom", "home")
    except Exception as e:
        assert (
            repr(e)
            == "KeyError('Given resource does not contain a key called telecom')"
        )

    # Failure case: default field out of range
    try:
        get_field(patient, "telecom", "office", 8)
    except Exception as e:
        assert (
            repr(e)
            == "IndexError('Index of provided field default is out of range for field array')"  # noqa
        )


def test_get_one_line_address():
    assert get_one_line_address({}) == ""
    address = {
        "line": ["1234 Silversun Strip"],
        "city": "Zakera Ward",
        "state": "Citadel",
        "postalCode": "99999",
    }
    assert (
        get_one_line_address(address)
        == "1234 Silversun Strip Zakera Ward, Citadel 99999"
    )
