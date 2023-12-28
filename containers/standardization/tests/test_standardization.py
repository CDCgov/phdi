import copy
import json
import pathlib
from unittest import mock

import pytest
from fastapi.testclient import TestClient
from smartystreets_python_sdk.us_street.candidate import Candidate
from smartystreets_python_sdk.us_street.metadata import Metadata
from smartystreets_python_sdk.us_street.components import Components

from app.main import app
from app.utils import (
    GeocodeResult,
    SmartyGeocodeClient,
    standardize_name,
    standardize_country_code,
    standardize_phone,
    standardize_phones_in_bundle,
    _standardize_phones_in_resource,
    _extract_countries_from_resource,
    read_json_from_assets,
    _standardize_date,
    _validate_date,
)

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


@pytest.fixture
def expected_geocode_result():
    return GeocodeResult(
        line=["1428 Post Aly"],
        city="Seattle",
        state="WA",
        lat=47.608479,
        lng=-122.340202,
        county_fips="53033",
        county_name="King",
        postal_code="98101",
        precision="Rooftop",
    )


@pytest.fixture
def smarty_geocode_client():
    smarty_auth_id = mock.Mock()
    smarty_auth_token = mock.Mock()
    return SmartyGeocodeClient(smarty_auth_id, smarty_auth_token)


@pytest.fixture
def mock_smarty_candidate():
    candidate = Candidate({})
    candidate.delivery_line_1 = "1428 Post Aly"
    candidate.components = Components(
        {
            "primary_number": "1428",
            "street_name": "Post",
            "street_suffix": "Aly",
            "city_name": "Seattle",
            "state_abbreviation": "WA",
            "zipcode": "98101",
            "plus4_code": "2034",
        }
    )
    candidate.metadata = Metadata(
        {
            "latitude": 47.608479,
            "longitude": -122.340202,
            "county_fips": "53033",
            "county_name": "King",
            "precision": "Rooftop",
        }
    )
    return candidate


def test_parse_smarty_result_success(mock_smarty_candidate):
    candidate = mock_smarty_candidate

    lookup = mock.Mock()
    lookup.result = [candidate]
    encoded_result = SmartyGeocodeClient._parse_smarty_result(lookup)

    assert encoded_result.line == ["1428 Post Aly"]
    assert encoded_result.city == "Seattle"
    assert encoded_result.state == "WA"
    assert encoded_result.lat == 47.608479
    assert encoded_result.lng == -122.340202
    assert encoded_result.county_fips == "53033"
    assert encoded_result.county_name == "King"
    assert encoded_result.postal_code == "98101"
    assert encoded_result.precision == "Rooftop"


def test_parse_smarty_result_failure():
    # no result from the API
    lookup_no_result = mock.Mock()
    lookup_no_result.result = None
    assert SmartyGeocodeClient._parse_smarty_result(lookup_no_result) is None

    # incomplete data in the result
    lookup_incomplete = mock.Mock()
    candidate_incomplete = Candidate({})
    candidate_incomplete.delivery_line_1 = "1428 Post Aly"
    lookup_incomplete.result = [candidate_incomplete]

    assert SmartyGeocodeClient._parse_smarty_result(lookup_incomplete) is None


def test_geocode_from_str(
    smarty_geocode_client, mock_smarty_candidate, expected_geocode_result
):
    assert smarty_geocode_client.client is not None

    with mock.patch.object(
        smarty_geocode_client.client, "send_lookup"
    ) as mock_send_lookup:
        # provide a function that adds results to the existing object
        def fill_in_result(*args, **kwargs):
            args[0].result = [mock_smarty_candidate]

        mock_send_lookup.side_effect = fill_in_result

        assert expected_geocode_result == smarty_geocode_client.geocode_from_str(
            "1428 Post Aly Seattle WA 98101"
        )
        mock_send_lookup.assert_called()


def test_geocode_from_dict(
    smarty_geocode_client, mock_smarty_candidate, expected_geocode_result
):
    assert smarty_geocode_client.client is not None

    with mock.patch.object(
        smarty_geocode_client.client, "send_lookup"
    ) as mock_send_lookup:
        # provide a function that adds results to the existing object
        def fill_in_result(*args, **kwargs):
            args[0].result = [mock_smarty_candidate]

        mock_send_lookup.side_effect = fill_in_result

        input_dict = {
            "street": "1428 Post Aly",
            "city": "Seattle",
            "state": "WA",
            "zip": "98101",
        }

        assert expected_geocode_result == smarty_geocode_client.geocode_from_dict(
            input_dict
        )
        mock_send_lookup.assert_called()


def test_blank_geocode_inputs(smarty_geocode_client):
    assert smarty_geocode_client.client is not None

    # test geocode_from_str with empty string
    with pytest.raises(ValueError) as e:
        smarty_geocode_client.geocode_from_str("")
    assert "Address must include street number and name at a minimum" in str(e.value)

    # test geocode_from_dict with empty dict
    with pytest.raises(ValueError) as e:
        smarty_geocode_client.geocode_from_dict({})
    assert "Address must include street number and name at a minimum" in str(e.value)
