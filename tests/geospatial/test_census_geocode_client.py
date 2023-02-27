from phdi.geospatial.core import GeocodeResult
from phdi.geospatial.census import CensusGeocodeClient
import json
import pathlib
from unittest import mock
from unittest.mock import patch
import pytest
import requests


@patch("phdi.geospatial.census.http_request_with_retry")
def test_call_census_api(mock_request):
    mock_response = mock.Mock()
    mock_response.status_code = 404
    mock_request.return_value = mock_response

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


def test_parse_census_result_success():
    censusResponseFullAddress = json.load(
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "censusResponseFullAddress.json"
        )
    )

    encoded_result = CensusGeocodeClient._parse_census_result(censusResponseFullAddress)

    assert encoded_result.line == ["239 GREENE ST"]
    assert encoded_result.city == "NEW YORK"
    assert encoded_result.state == "NY"
    assert encoded_result.lat == 40.72962831414409
    assert encoded_result.lng == -73.9954428687588
    assert encoded_result.county_fips == "36061"
    assert encoded_result.county_name == "New York"
    assert encoded_result.postal_code == "10003"


def test_parse_census_result_failure():
    censusResponseFullAddress_noAddressMatch = json.load(
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "censusResponseFullAddress.json"
        )
    )

    # Test when addressMatches is an empty list
    censusResponseFullAddress_noAddressMatch["addressMatches"] = []
    assert (
        CensusGeocodeClient._parse_census_result(
            censusResponseFullAddress_noAddressMatch
        )
        is None
    )


def test_geocode_from_str():
    census_client = CensusGeocodeClient()
    address = "239 Greene Street, New York, NY, 10003"
    censusResponseFullAddress = json.load(
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "censusResponseFullAddress.json"
        )
    )
    census_client._call_census_api = mock.Mock()
    census_client._call_census_api.return_value = censusResponseFullAddress

    geocoded_response = GeocodeResult(
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
    assert geocoded_response == census_client.geocode_from_str(address)

    # Test ambiguous address/address with multiple matches
    address = "659 Centre St"
    address_response = {
        "address": address,
    }
    census_client._call_census_api.return_value = address_response

    assert census_client.geocode_from_str(address) is None

    # Test empty string address
    address = ""
    geocoded_response = None
    with pytest.raises(ValueError) as e:
        geocoded_response = census_client.geocode_from_str(address)
    assert "Address must include street number and name at a minimum" in str(e.value)
    assert geocoded_response is None


def test_geocode_from_dict():
    censusResponseFullAddress = json.load(
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "censusResponseFullAddress.json"
        )
    )

    census_client = CensusGeocodeClient()
    census_client._call_census_api = mock.Mock()
    census_client._call_census_api.return_value = censusResponseFullAddress

    # Test address with full, complete information
    full_address_dict = {
        "street": "239 Greene Street",
        "city": "New York",
        "state": "NY",
        "zip": "10003",
    }

    geocoded_response = GeocodeResult(
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
    census_client._call_census_api.return_value = ambiguous_address_dict
    assert census_client.geocode_from_dict(ambiguous_address_dict) is None

    # Test malformed input input (e.g., zipcode == ABC)
    malformed_input_dict = {
        "street": "239",
        "city": "1234",
        "state": "ABC",
        "zip": "00000",
    }
    assert census_client.geocode_from_dict(malformed_input_dict) is None
