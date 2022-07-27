from phdi_building_blocks.fhir_wrappers.geospatial.smarty import SmartyGeocodeClient
from phdi_building_blocks.geospatial.geospatial import GeocodeResult

from smartystreets_python_sdk.us_street.candidate import Candidate
from smartystreets_python_sdk.us_street.metadata import Metadata
from smartystreets_python_sdk.us_street.components import Components

from unittest import mock
import json
import pathlib
import copy


def test_geocode_resource():
    auth_id = mock.Mock()
    auth_token = mock.Mock()
    smarty_client = SmartyGeocodeClient(auth_id, auth_token)
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

    geocoded_response = GeocodeResult(
        street=["123 FAKE ST"],
        city="New York",
        state="NY",
        lat=45.123,
        lng=-70.234,
        county_fips="36061",
        county_name="New York",
        zipcode="10001",
        precision="Zip9",
    )

    bundle = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "patient_bundle.json"
        )
    )
    patient = bundle["entry"][1]["resource"]
    standardized_patient = copy.deepcopy(patient)
    address = standardized_patient["address"][0]
    address["line"] = geocoded_response.street
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

    smarty_client.client.send_lookup = mock.Mock()
    smarty_client.client.send_lookup.side_effect = fill_in_result

    assert standardized_patient == smarty_client.geocode_resource(patient)
    smarty_client.client.send_lookup.assert_called()


def test_geocode_bundle():
    auth_id = mock.Mock()
    auth_token = mock.Mock()
    smarty_client = SmartyGeocodeClient(auth_id, auth_token)
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

    geocoded_response = GeocodeResult(
        street=["123 FAKE ST"],
        city="New York",
        state="NY",
        lat=45.123,
        lng=-70.234,
        county_fips="36061",
        county_name="New York",
        zipcode="10001",
        precision="Zip9",
    )

    bundle = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "patient_bundle.json"
        )
    )
    standardized_bundle = copy.deepcopy(bundle)
    patient = standardized_bundle["entry"][1]["resource"]
    address = patient["address"][0]
    address["line"] = geocoded_response.street
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

    smarty_client.client.send_lookup = mock.Mock()
    smarty_client.client.send_lookup.side_effect = fill_in_result

    assert standardized_bundle == smarty_client.geocode_bundle(bundle)
    smarty_client.client.send_lookup.assert_called()
