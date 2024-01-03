import copy
import json
import pathlib

import pytest
from app.main import app
from app.utils import _extract_countries_from_resource
from app.utils import _standardize_date
from app.utils import _standardize_phones_in_resource
from app.utils import _validate_date
from app.utils import read_json_from_assets
from app.utils import standardize_country_code
from app.utils import standardize_name
from app.utils import standardize_phone
from app.utils import standardize_phones_in_bundle
from fastapi.testclient import TestClient

client = TestClient(app)


@pytest.fixture
def single_patient_bundle():
    return read_json_from_assets("single_patient_bundle.json")


def test_health_check():
    actual_response = client.get("/")
    assert actual_response.status_code == 200
    assert actual_response.json() == {
        "status": "OK",
    }


def test_standardize_name():
    # Basic case of input string
    raw_text = " 12 dIBbs is ReaLLy KEWL !@#$ 34"
    assert (
        standardize_name(raw_text, trim=True, case="lower", remove_numbers=False)
        == "12 dibbs is really kewl  34"
    )
    assert (
        standardize_name(raw_text, trim=True, remove_numbers=True, case="title")
        == "Dibbs Is Really Kewl"
    )
    assert (
        standardize_name(raw_text, trim=False, remove_numbers=True, case="title")
        == "  Dibbs Is Really Kewl  "
    )
    # Now check that it handles list inputs
    names = ["Johnny T. Walker", " Paul bunYAN", "J;R;R;tOlK.iE87n 999"]
    assert standardize_name(names, trim=True, remove_numbers=False) == [
        "JOHNNY T WALKER",
        "PAUL BUNYAN",
        "JRRTOLKIE87N 999",
    ]


@pytest.mark.parametrize(
    "input_date, format_string, future, expected",
    [
        ("1977-11-21", None, False, "1977-11-21"),
        ("1980-01-31", None, False, "1980-01-31"),
        ("1977/11/21", "%Y/%m/%d", False, "1977-11-21"),
        ("1980/01/31", "%Y/%m/%d", False, "1980-01-31"),
        ("01/1980/31", "%m/%Y/%d", False, "1980-01-31"),
        ("11-1977-21", "%m-%Y-%d", False, "1977-11-21"),
    ],
)
def test_standardize_date(input_date, format_string, future, expected):
    if format_string:
        assert _standardize_date(input_date, format_string, future) == expected
    else:
        assert _standardize_date(input_date, future=future) == expected


def test_standardize_date_invalid():
    with pytest.raises(ValueError) as e:
        _standardize_date("blah")
    assert "Invalid date format or missing components in date: blah" in str(e.value)


def test_standardize_date_format_mismatch():
    with pytest.raises(ValueError) as e:
        _standardize_date("abc-def-ghi", "%Y-%m-%d")
    assert "Invalid date format supplied:" in str(e.value)

    with pytest.raises(ValueError) as e:
        _standardize_date("1980-01-31", "%H:%M:%S")
    assert "Invalid date format or missing components in date:" in str(e.value)


@pytest.mark.parametrize(
    "year, month, day, allow_future, expected",
    [
        ("1980", "10", "15", False, True),
        ("3030", "10", "15", False, True),
        ("3030", "10", "15", True, False),
        ("2005", "15", "10", False, False),
        ("2005", "02", "30", False, False),
    ],
)
def test_validate_date(year, month, day, allow_future, expected):
    assert _validate_date(year, month, day, allow_future) == expected


def test_standardize_country_code():
    assert standardize_country_code("US") == "US"
    assert standardize_country_code("USA") == "US"
    assert standardize_country_code("United States of America") == "US"
    assert standardize_country_code("United states ") == "US"
    assert standardize_country_code("US", "alpha_3") == "USA"
    assert standardize_country_code("USA", "numeric") == "840"

    # Edge case testing: nonsense code and empty string
    assert standardize_country_code("zzz") is None
    assert standardize_country_code("") is None


def test_standardize_phone():
    # Working examples of "real" numbers
    assert standardize_phone("555-654-9876") == "+15556549876"
    assert standardize_phone("555 654 9876") == "+15556549876"
    # Now supply country information
    assert standardize_phone("123.234.6789", ["US"]) == "+11232346789"
    assert standardize_phone("798.612.3456", ["GB"]) == "+447986123456"
    # Now do it as a list
    assert standardize_phone(["555-654-1234", "919876543210"], countries=["IN"]) == [
        "+915556541234",
        "+919876543210",
    ]
    # Make sure we catch edge cases and bad inputs
    assert standardize_phone("") == ""
    assert standardize_phone(" ") == ""
    assert standardize_phone("gibberish") == ""
    assert standardize_phone("1234567890987654321") == ""
    assert standardize_phone("123") == ""


def test_standardize_phones():
    raw_bundle = json.load(
        open(
            pathlib.Path(__file__).parent.parent / "assets" / "test_patient_bundle.json"
        )
    )

    # Case where we pass in a whole FHIR bundle
    standardized_bundle = copy.deepcopy(raw_bundle.copy())
    patient = standardized_bundle["entry"][1]["resource"]
    patient["telecom"][0]["value"] = "+11234567890"
    assert standardize_phones_in_bundle(raw_bundle) == standardized_bundle

    # Case where we pass in a whole FHIR bundle and do not overwrite the data
    standardized_bundle = copy.deepcopy(raw_bundle.copy())
    patient = standardized_bundle["entry"][1]["resource"]
    patient["telecom"][0]["value"] = "+11234567890"
    assert (
        standardize_phones_in_bundle(raw_bundle, overwrite=False) == standardized_bundle
    )

    # Case where we provide only a single resource
    patient_resource = raw_bundle["entry"][1]["resource"]
    standardized_patient = copy.deepcopy(patient_resource)
    standardized_patient["telecom"][0]["value"] = "+11234567890"
    assert standardize_phones_in_bundle(patient_resource) == standardized_patient

    # Case where we provide only a single resource and do not overwrite the data
    patient_resource = raw_bundle["entry"][1]["resource"]
    standardized_patient = copy.deepcopy(patient_resource)
    standardized_patient["telecom"][0]["value"] = "+11234567890"
    assert (
        standardize_phones_in_bundle(patient_resource, overwrite=False)
        == standardized_patient
    )

    # Case where the input data has no country information in the address
    patient_resource = raw_bundle["entry"][1]["resource"]
    patient_resource.get("address")[0].pop("country")
    assert patient_resource.get("address")[0].get("country") is None
    standardized_patient = copy.deepcopy(patient_resource)
    standardized_patient["telecom"][0]["value"] = "+11234567890"
    assert standardize_phones_in_bundle(patient_resource) == standardized_patient

    # Case where the input data has no country information in the address and we do not
    # overwrite the data
    patient_resource = raw_bundle["entry"][1]["resource"]
    assert patient_resource.get("address")[0].get("country") is None
    standardized_patient = copy.deepcopy(patient_resource)
    standardized_patient["telecom"][0]["value"] = "+11234567890"
    assert (
        standardize_phones_in_bundle(patient_resource, overwrite=False)
        == standardized_patient
    )


def test_standardize_phones_in_resource():
    raw_bundle = json.load(
        open(
            pathlib.Path(__file__).parent.parent / "assets" / "test_patient_bundle.json"
        )
    )
    patient_resource = raw_bundle["entry"][1]["resource"]
    standardized_patient = copy.deepcopy(patient_resource)
    standardized_patient["telecom"][0]["value"] = "+11234567890"
    assert _standardize_phones_in_resource(patient_resource) == standardized_patient


def test_extract_countries_from_resource():
    raw_bundle = json.load(
        open(
            pathlib.Path(__file__).parent.parent / "assets" / "test_patient_bundle.json"
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
