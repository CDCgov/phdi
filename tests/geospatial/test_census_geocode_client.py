# from unittest import mock
from phdi.geospatial.core import GeocodeResult
from phdi.geospatial.census import CensusGeocodeClient
import json
import pathlib


def test_parse_census_result_success():
    censusResponseFullAddress = json.load(
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "censusResponseFullAddress.json"
        )
    )

    encoded_result = CensusGeocodeClient._parse_census_result(censusResponseFullAddress)

    assert encoded_result.line == ["239 GREENE ST", "NEW YORK", "NY", "10003"]
    assert encoded_result.city == "NEW YORK"
    assert encoded_result.state == "NY"
    assert encoded_result.lat == 40.72962831414409
    assert encoded_result.lng == -73.9954428687588
    assert encoded_result.county_fips == "36061"
    assert encoded_result.county_name == "New York"
    assert encoded_result.postal_code == "10003"


def test_parse_census_result_failure():
    censusResponseFullAddress = json.load(
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "censusResponseFullAddress.json"
        )
    )

    # Test when addressMatches is an empty list
    censusResponseFullAddress_noAddressMatch = censusResponseFullAddress
    censusResponseFullAddress_noAddressMatch["addressMatches"] = []
    assert (
        CensusGeocodeClient._parse_census_result(
            censusResponseFullAddress_noAddressMatch
        )
        is None
    )


def test_geocode_from_str():
    census_client = CensusGeocodeClient()
    address = "659 Centre St, Boston, MA 02130"

    geocoded_response = GeocodeResult(
        line=["659 CENTRE ST", "BOSTON", "MA", "02130"],
        city="BOSTON",
        state="MA",
        postal_code="02130",
        county_fips="25025",
        lat=42.31304390969022,
        lng=-71.11410863903707,
        district=None,
        country=None,
        county_name="Suffolk",
        precision=None,
        geoid="250251201031000",
        census_tract="1201.03",
        census_block="1000",
    )
    assert geocoded_response == census_client.geocode_from_str(address)

    # Test ambiguous address/address with multiple matches
    address = "659 Centre St"
    assert census_client.geocode_from_str(address) is None

    # Test empty string address
    address = ""
    geocode_result = None
    try:
        geocode_result = census_client.geocode_from_str(address)
    except Exception as e:
        assert (
            repr(e) == "Exception('Must include street number and name at a minimum')"
        )
        assert geocode_result is None


def test_geocode_from_dict():
    census_client = CensusGeocodeClient()
    # Test address with full, complete information
    full_address_dict = {
        "street": "239 Greene Street",
        "city": "New York",
        "state": "NY",
        "zip": "10003",
    }

    geocoded_response = GeocodeResult(
        line=["239 GREENE ST", "NEW YORK", "NY", "10003"],
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

    # Test address with missing street num and name
    missing_street_dict = {
        "city": "New York",
        "state": "NY",
        "zip": "10003",
    }
    try:
        geocoded_response == census_client.geocode_from_dict(missing_street_dict)
    except Exception as e:
        assert (
            repr(e) == "Exception('Must include street number and name at a minimum')"
        )

    # Test ambiguous address
    ambiguous_address_dict = {"street": "123 Main Street"}
    assert census_client.geocode_from_dict(ambiguous_address_dict) is None

    # Test malformed input input (e.g., zipcode == ABC)
    malformed_input_dict = {
        "street": "239",
        "city": "1234",
        "state": "ABC",
        "zip": "00000",
    }
    assert census_client.geocode_from_dict(malformed_input_dict) is None
