import json
import pathlib
import copy
from unittest import mock

from smartystreets_python_sdk.us_street.candidate import Candidate
from smartystreets_python_sdk.us_street.metadata import Metadata
from smartystreets_python_sdk.us_street.components import Components

from phdi_building_blocks.geo import (
    get_geocoder_result,
    geocode_patients,
)
from phdi_building_blocks.geo import GeocodeResult


def test_get_geocoder_result_success():
    """
    Make sure to return the correct dict attribs from the SmartyStreets
    response object on a successful call
    """

    # SmartyStreets fills in a request object inline, so let's fake that
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

    client = mock.Mock()
    client.send_lookup.side_effect = fill_in_result

    assert {
        "address": ["123 FAKE ST"],
        "city": "New York",
        "state": "NY",
        "lat": 45.123,
        "lng": -70.234,
        "county_fips": "36061",
        "county_name": "New York",
        "zipcode": "10001",
        "precision": "Zip9",
    } == get_geocoder_result("123 Fake St, New York, NY 10001", client)

    client.send_lookup.assert_called()


def test_get_geocoder_result_failure():
    """If it doesn't fill in results, return None"""
    assert get_geocoder_result("123 Nowhere St, Atlantis GA", mock.Mock()) is None


@mock.patch("phdi_building_blocks.geo.get_geocoder_result")
def test_geocode_patients(patched_geocoder):
    raw_bundle = json.load(
        open(pathlib.Path(__file__).parent / "assets" / "patient_bundle.json")
    )
    geocoded_response = GeocodeResult(
        address=["123 FAKE ST"],
        city="New York",
        state="NY",
        lat=45.123,
        lng=-70.234,
        county_fips="36061",
        county_name="New York",
        zipcode="10001",
        precision="Zip9",
    )

    standardized_bundle = copy.deepcopy(raw_bundle)
    patient = standardized_bundle["entry"][1]["resource"]
    address = patient["address"][0]
    address["line"] = geocoded_response.address
    address["city"] = geocoded_response.city
    address["state"] = geocoded_response.state
    address["postalCode"] = geocoded_response.zipcode
    address["extension"] = []
    address["extension"].append(
        {
            "url": "http://hl7.org/fhir/StructureDefinition/geolocation",
            "extension": [
                {"url": "latitude", "valueDecimal": geocoded_response.lat},
                {"url": "longitude", "valueDecimal": geocoded_response.lng},
            ],
        }
    )

    patched_geocoder.return_value = geocoded_response

    assert geocode_patients(raw_bundle, mock.Mock()) == standardized_bundle
