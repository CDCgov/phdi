from unittest import mock

import pytest
from smartystreets_python_sdk.us_street.candidate import Candidate
from smartystreets_python_sdk.us_street.components import Components
from smartystreets_python_sdk.us_street.metadata import Metadata

from phdi.geospatial.core import GeocodeResult
from phdi.geospatial.smarty import SmartyGeocodeClient


def test_parse_smarty_result_success():
    candidate = Candidate({})
    candidate.delivery_line_1 = "123 FAKE ST"
    candidate.delivery_line_2 = "UNIT 221B"
    candidate.metadata = Metadata(
        {
            "latitude": 45.123,
            "longitude": -70.234,
            "county_fips": "36061",
            "county_name": "New York",
            "precision": "Zip9",
        }
    )

    candidate.components = Components(
        {"zipcode": "10001", "city_name": "New York", "state_abbreviation": "NY"}
    )

    lookup = mock.Mock()
    lookup.result = [candidate]
    encoded_result = SmartyGeocodeClient._parse_smarty_result(lookup)

    assert encoded_result.line == ["123 FAKE ST", "UNIT 221B"]
    assert encoded_result.city == "New York"
    assert encoded_result.state == "NY"
    assert encoded_result.lat == 45.123
    assert encoded_result.lng == -70.234
    assert encoded_result.county_fips == "36061"
    assert encoded_result.county_name == "New York"
    assert encoded_result.postal_code == "10001"
    assert encoded_result.precision == "Zip9"


def test_parse_smarty_result_failure():
    lookup = mock.Mock()
    lookup.result = None
    assert SmartyGeocodeClient._parse_smarty_result(lookup) is None

    candidate = Candidate({})
    candidate.delivery_line_1 = "123 FAKE ST"
    candidate.metadata = Metadata(
        {
            "county_fips": "36061",
            "county_name": "New York",
            "precision": "Zip9",
        }
    )
    lookup.result = [candidate]
    assert SmartyGeocodeClient._parse_smarty_result(lookup) is None


def test_geocode_from_str():
    smarty_auth_id = mock.Mock()
    smarty_auth_token = mock.Mock()
    smarty_client = SmartyGeocodeClient(smarty_auth_id, smarty_auth_token)
    assert smarty_client.client is not None

    candidate = Candidate({})
    candidate.delivery_line_1 = "123 FAKE ST"
    candidate.metadata = Metadata(
        {
            "latitude": 45.123,
            "longitude": -70.234,
            "county_fips": "36061",
            "county_name": "New York",
            "precision": "Zip9",
        }
    )
    candidate.components = Components(
        {"zipcode": "10001", "city_name": "New York", "state_abbreviation": "NY"}
    )

    # Provide a function that adds results to the existing object
    def fill_in_result(*args, **kwargs):
        args[0].result = [candidate]

    smarty_client.client.send_lookup = mock.Mock()
    smarty_client.client.send_lookup.side_effect = fill_in_result

    geocoded_response = GeocodeResult(
        line=["123 FAKE ST"],
        city="New York",
        state="NY",
        lat=45.123,
        lng=-70.234,
        county_fips="36061",
        county_name="New York",
        postal_code="10001",
        precision="Zip9",
    )

    assert geocoded_response == smarty_client.geocode_from_str(
        "123 FAKE ST New York NY 10001"
    )
    smarty_client.client.send_lookup.assert_called()


def test_geocode_from_dict():
    smarty_auth_id = mock.Mock()
    smarty_auth_token = mock.Mock()
    smarty_client = SmartyGeocodeClient(smarty_auth_id, smarty_auth_token)
    assert smarty_client.client is not None

    candidate = Candidate({})
    candidate.delivery_line_1 = "123 FAKE ST"
    candidate.metadata = Metadata(
        {
            "latitude": 45.123,
            "longitude": -70.234,
            "county_fips": "36061",
            "county_name": "New York",
            "precision": "Zip9",
        }
    )
    candidate.components = Components(
        {"zipcode": "10001", "city_name": "New York", "state_abbreviation": "NY"}
    )

    # Provide a function that adds results to the existing object
    def fill_in_result(*args, **kwargs):
        args[0].result = [candidate]

    smarty_client.client.send_lookup = mock.Mock()
    smarty_client.client.send_lookup.side_effect = fill_in_result

    geocoded_response = GeocodeResult(
        line=["123 FAKE ST"],
        city="New York",
        state="NY",
        lat=45.123,
        lng=-70.234,
        county_fips="36061",
        county_name="New York",
        postal_code="10001",
        precision="Zip9",
    )

    input_dict = {
        "street": "123 FAKE ST",
        "city": "New York",
        "state": "NY",
        "zip": "10001",
    }
    assert geocoded_response == smarty_client.geocode_from_dict(input_dict)
    smarty_client.client.send_lookup.assert_called()


def test_blank_geocode_inputs():
    smarty_auth_id = mock.Mock()
    smarty_auth_token = mock.Mock()
    smarty_client = SmartyGeocodeClient(smarty_auth_id, smarty_auth_token)
    assert smarty_client.client is not None

    geocoded_response = None
    with pytest.raises(ValueError) as e:
        geocoded_response = smarty_client.geocode_from_str("")
    assert "Address must include street number and name at a minimum" in str(e.value)
    assert geocoded_response is None

    with pytest.raises(ValueError) as e:
        geocoded_response = smarty_client.geocode_from_dict({})
    assert "Address must include street number and name at a minimum" in str(e.value)
    assert geocoded_response is None
