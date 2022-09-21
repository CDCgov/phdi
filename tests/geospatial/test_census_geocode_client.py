# from unittest import mock
from phdi.geospatial.core import GeocodeResult
from phdi.geospatial.census import CensusGeocodeClient
import json
import pathlib


def test_parse_smarty_result_success():
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
    assert encoded_result.precision == "zip5"


# def test_parse_smarty_result_failure():
#     lookup = None
#     assert CensusGeocodeClient._parse_census_result(lookup) is None


# def test_geocode_from_str(): # Come back to this
#     census_client = CensusGeocodeClient()
#     address = "659 Centre St, Boston, MA 02130"

#     geocoded_response = GeocodeResult(
#         line=["659 CENTRE ST", "BOSTON", "MA", "02130"],
#         city="BOSTON",
#         state="MA",
#         lat=45.123,
#         lng=-70.234,
#         county_fips="36061",
#         county_name="Suffolk",
#         postal_code="02130",
#         precision="Zip5",
#     )

#     assert geocoded_response == census_client.geocode_from_str(address)
#     # smarty_client.client.send_lookup.assert_called()


# def test_geocode_from_dict():
#     auth_id = mock.Mock()
#     auth_token = mock.Mock()
#     smarty_client = SmartyGeocodeClient(auth_id, auth_token)
#     assert smarty_client.client is not None

#     candidate = Candidate({})
#     candidate.delivery_line_1 = "123 FAKE ST"
#     candidate.metadata = Metadata(
#         {
#             "latitude": 45.123,
#             "longitude": -70.234,
#             "county_fips": "36061",
#             "county_name": "New York",
#             "precision": "Zip9",
#         }
#     )
#     candidate.components = Components(
#         {"zipcode": "10001", "city_name": "New York", "state_abbreviation": "NY"}
#     )

#     # Provide a function that adds results to the existing object
#     def fill_in_result(*args, **kwargs):
#         args[0].result = [candidate]

#     smarty_client.client.send_lookup = mock.Mock()
#     smarty_client.client.send_lookup.side_effect = fill_in_result

#     geocoded_response = GeocodeResult(
#         line=["123 FAKE ST"],
#         city="New York",
#         state="NY",
#         lat=45.123,
#         lng=-70.234,
#         county_fips="36061",
#         county_name="New York",
#         postal_code="10001",
#         precision="Zip9",
#     )

#     input_dict = {
#         "street": "123 FAKE ST",
#         "city": "New York",
#         "state": "NY",
#         "zip": "10001",
#     }
#     assert geocoded_response == smarty_client.geocode_from_dict(input_dict)
#     smarty_client.client.send_lookup.assert_called()


# def test_blank_geocode_inputs():
#     auth_id = mock.Mock()
#     auth_token = mock.Mock()
#     smarty_client = SmartyGeocodeClient(auth_id, auth_token)
#     assert smarty_client.client is not None

#     geocode_result = None
#     try:
#         geocode_result = smarty_client.geocode_from_str("")
#     except Exception as e:
#         assert repr(e) == "Exception('Cannot geocode an empty string')"
#         assert geocode_result is None

#     try:
#         geocode_result = smarty_client.geocode_from_dict({})
#     except Exception as e:
#         assert repr(e) == "Exception('Must include street information at a minimum')"
#         assert geocode_result is None
