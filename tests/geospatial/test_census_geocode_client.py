import json
import pathlib

import pytest
import requests

from phdi.geospatial.census import CensusGeocodeClient
from phdi.geospatial.core import GeocodeResult

CENSUS_RESPONSE_FILE = (
    pathlib.Path(__file__).parent.parent
    / "assets"
    / "geospatial"
    / "censusResponseFullAddress.json"
)


@pytest.fixture
def census_response_data():
    with open(CENSUS_RESPONSE_FILE) as file:
        return json.load(file)


@pytest.fixture
def geocoded_response():
    return GeocodeResult(
        line=["239 GREENE ST"],
        city="NEW YORK",
        state="NY",
        postal_code="10003",
        county_fips="36061",
        lat=40.72962831414409,
        lng=-73.9954428687588,
        district=None,
        country=None,
        county_name="New York",
        precision=None,
        geoid="360610059003005",
        census_tract="59",
        census_block="3005",
    )


def mock_call_census_api(census_response_data, *args, **kwargs):
    return census_response_data


def mock_ambiguous_address(*args, **kwargs):
    return {"addressMatches": []}


def test_call_census_api(monkeypatch):
    class MockResponse:
        status_code = 404

    def mock_http_request_with_retry(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(
        "phdi.geospatial.census.http_request_with_retry", mock_http_request_with_retry
    )

    url = (
        "https://geocoding.geo.census.gov/geocoder/geographies/"
        + "onelineaddress?address=239+Greene+St+New+York%2C+NY"
        + "&benchmark=Public_AR_Census2020"
        + "&vintage=Census2020_Census2020"
        + "&layers=[10]"
        + "&format=json"
    )

    with pytest.raises(requests.exceptions.HTTPError) as e:
        CensusGeocodeClient._call_census_api(url)
        assert "<ExceptionInfo HTTPError() tblen=2>" in str(e.value)


def test_parse_census_result_success(census_response_data):
    encoded_result = CensusGeocodeClient._parse_census_result(census_response_data)

    assert encoded_result.line == ["239 GREENE ST"]
    assert encoded_result.city == "NEW YORK"
    assert encoded_result.state == "NY"
    assert encoded_result.lat == 40.72962831414409
    assert encoded_result.lng == -73.9954428687588
    assert encoded_result.county_fips == "36061"
    assert encoded_result.county_name == "New York"
    assert encoded_result.postal_code == "10003"


def test_parse_census_result_failure(census_response_data):
    census_response_data["addressMatches"] = []
    assert CensusGeocodeClient._parse_census_result(census_response_data) is None


def test_geocode_from_str(monkeypatch, census_response_data, geocoded_response):
    address = "239 Greene Street, New York, NY, 10003"
    census_client = CensusGeocodeClient()

    monkeypatch.setattr(
        census_client,
        "_call_census_api",
        lambda *args, **kwargs: mock_call_census_api(
            census_response_data, *args, **kwargs
        ),
    )

    assert geocoded_response == census_client.geocode_from_str(address)

    # Test ambiguous address/address with multiple matches
    ambiguous_address = "659 Centre St"
    monkeypatch.setattr(census_client, "_call_census_api", mock_ambiguous_address)
    assert census_client.geocode_from_str(ambiguous_address) is None

    # Test empty string address
    address = ""
    geocoded_response = None
    with pytest.raises(ValueError) as e:
        geocoded_response = census_client.geocode_from_str(address)
    assert "Address must include street number and name at a minimum" in str(e.value)
    assert geocoded_response is None


def test_geocode_from_dict(monkeypatch, census_response_data, geocoded_response):
    census_client = CensusGeocodeClient()

    # set the default mock response
    monkeypatch.setattr(
        census_client,
        "_call_census_api",
        lambda *args, **kwargs: mock_call_census_api(
            census_response_data, *args, **kwargs
        ),
    )

    # Test address with full, complete information
    full_address_dict = {
        "street": "239 Greene Street",
        "city": "New York",
        "state": "NY",
        "zip": "10003",
    }

    assert geocoded_response == census_client.geocode_from_dict(full_address_dict)

    # Test address with missing zip code
    missing_zip_dict = {
        "street": "239 Greene Street",
        "city": "New York",
        "state": "NY",
    }
    assert geocoded_response == census_client.geocode_from_dict(missing_zip_dict)

    # Test address with missing street num and name
    missing_street_dict = {
        "city": "New York",
        "state": "NY",
        "zip": "10003",
    }
    geocoded_response = None

    with pytest.raises(ValueError) as e:
        geocoded_response = census_client.geocode_from_dict(missing_street_dict)
    assert "Address must include street number and name at a minimum" in str(e.value)
    assert geocoded_response is None

    # Test ambiguous address
    ambiguous_address_dict = {"street": "123 Main Street"}
    monkeypatch.setattr(census_client, "_call_census_api", mock_ambiguous_address)
    assert census_client.geocode_from_dict(ambiguous_address_dict) is None

    # Test malformed input input (e.g., zipcode == ABC)
    malformed_input_dict = {
        "street": "239",
        "city": "1234",
        "state": "ABC",
        "zip": "00000",
    }
    assert census_client.geocode_from_dict(malformed_input_dict) is None
