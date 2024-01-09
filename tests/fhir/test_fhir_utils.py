import json
import pathlib

import pytest

from phdi.fhir.utils import apply_selection_criteria
from phdi.fhir.utils import find_entries_by_resource_type
from phdi.fhir.utils import get_field
from phdi.fhir.utils import get_one_line_address


def test_apply_selection_criteria():
    with pytest.raises(ValueError) as e:
        apply_selection_criteria([], "invalid")
        assert (
            'is not a valid option. Must be one of "first", "last", or "random"'
            in str(e.value)
        )
    selection_criteria_test_list = ["one", "two", "three"]
    assert apply_selection_criteria(selection_criteria_test_list, "first") == "one"
    assert apply_selection_criteria(selection_criteria_test_list, "last") == "three"
    assert (
        apply_selection_criteria(selection_criteria_test_list, "random")
        in selection_criteria_test_list
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
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "general"
            / "patient_bundle.json"
        )
    )
    found_patients = find_entries_by_resource_type(bundle, "Patient")
    assert len(found_patients) == 1
    assert found_patients[0].get("resource").get("resourceType") == "Patient"


def test_get_field_valid_inputs():
    bundle = json.load(
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "general"
            / "patient_bundle.json"
        )
    )
    patient = bundle["entry"][1]["resource"]

    assert get_field(patient, field="telecom", use="home") == {
        "use": "home",
        "system": "phone",
        "value": "123-456-7890",
    }

    assert get_field(
        patient, field="telecom", use="mobile", require_use=False, index=2
    ) == {
        "value": "johndanger@doe.net",
        "system": "email",
    }

    assert get_field(patient, field="telecom", use="mobile", require_use=True) is None


def test_get_field_invalid_inputs():
    bundle = json.load(
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "general"
            / "patient_bundle.json"
        )
    )
    patient = bundle["entry"][1]["resource"]

    err_msg = "The field parameter must be a defined, non-empty string."
    with pytest.raises(ValueError, match=err_msg):
        get_field(patient, field="", use="home")

    err_msg = "The use parameter should be a defined, non-empty string. If you don't want to include a use, set the parameter to None."  # noqa
    with pytest.raises(ValueError, match=err_msg):
        get_field(patient, field="telecom", use="")

    err_msg = "This resource does not contain a field called telecom."
    with pytest.raises(KeyError, match=err_msg):
        get_field({}, field="telecom", use="home")


def test_get_field_indexes():
    bundle = json.load(
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "general"
            / "patient_bundle.json"
        )
    )
    patient = bundle["entry"][1]["resource"]

    assert get_field(patient, field="telecom", index=1) == {
        "use": "home",
        "system": "phone",
        "value": "123-456-7890",
    }

    assert get_field(patient, field="telecom", index=2) == {
        "value": "johndanger@doe.net",
        "system": "email",
    }

    # test that indexes that are too low give back the first element
    assert get_field(patient, field="telecom", index=0) == {
        "use": "home",
        "system": "phone",
        "value": "123-456-7890",
    }

    assert get_field(patient, field="telecom", index=-1) == {
        "use": "home",
        "system": "phone",
        "value": "123-456-7890",
    }

    # test that indexes that are too high give back the last element
    assert get_field(patient, field="telecom", index=10) == {
        "value": "johndanger@doe.net",
        "system": "email",
    }


def test_get_one_line_address():
    assert get_one_line_address({}) == ""
    address = {
        "line": ["1234 Silversun Strip"],
        "city": "Boston",
        "state": "Massachusetts",
        "postalCode": "99999",
    }
    assert (
        get_one_line_address(address)
        == "1234 Silversun Strip Boston, Massachusetts 99999"
    )
