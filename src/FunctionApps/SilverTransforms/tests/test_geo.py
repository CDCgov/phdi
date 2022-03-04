from unittest import mock

from smartystreets_python_sdk.us_street.candidate import Candidate
from smartystreets_python_sdk.us_street.metadata import Metadata
from smartystreets_python_sdk.us_street.components import Components

from Transform.geo import geocode, cached_geocode


def test_geocode():
    """
    Make sure to return the correct dict attribs from the SmartyStreets
    response object on a successful call
    """

    # SmartyStreets fills in a request object inline, so let's fake that
    candidate = Candidate({})
    candidate.delivery_line_1 = "123 FAKE ST"
    candidate.metadata = Metadata(
        {"latitude": 45.123, "longitude": -70.234, "county_fips": "36061"}
    )

    candidate.components = Components(
        {"zipcode": "10001", "city_name": "New York", "state_abbreviation": "NY"}
    )

    # Provide a function that adds results to the existing object
    def fill_in_result(*args, **kwargs):
        args[0].result = [candidate]

    client = mock.Mock()
    client.send_lookup.side_effect = fill_in_result

    assert {
        "address": ["123 FAKE ST"],
        "city": "New York",
        "state": "NY",
        "lat": 45.123,
        "lng": -70.234,
        "fips": "36061",
        "zipcode": "10001",
    } == geocode(client, "123 Fake St, New York, NY 10001")

    client.send_lookup.assert_called()


def test_failed_geocode():
    """If it doesn't fill in results, return None"""
    assert geocode(mock.Mock(), "123 Nowhere St, Atlantis GA") is None


@mock.patch("Transform.geo.geocode")
def test_cached_geocode(patched_geocode):
    """On a miss, we should geocode and then store it"""
    patched_geocode.return_value = {"hello": "world"}

    mock_collection = mock.Mock()
    mock_collection.find_one.return_value = None

    resp = cached_geocode(mock_collection, mock.Mock(), "123 Fake St")
    assert resp == {"hello": "world"}  # whatever the mock returns

    # Make sure we updated the cache
    mock_collection.find_one.assert_called_with({"key": "123FAKEST"})
    mock_collection.insert_one.assert_called()


@mock.patch("Transform.geo.geocode")
def test_cached_geocode_hit(patched_geocode):
    """On a hit, we shouldn't geocode at all"""
    mock_collection = mock.Mock()
    mock_collection.find_one.return_value = {
        "x": "some-key",
        "key": "should-remove-this",
    }

    resp = cached_geocode(mock_collection, mock.Mock(), "123 Fake St")
    patched_geocode.assert_not_called()

    assert resp == {"x": "some-key"}
