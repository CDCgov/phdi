from phdi_building_blocks.geospatial.geospatial import GeocodeClient, GeocodeResult

from smartystreets_python_sdk import StaticCredentials, ClientBuilder
from smartystreets_python_sdk import us_street
from smartystreets_python_sdk.us_street.lookup import Lookup

from typing import Union


class SmartyGeocodeClient(GeocodeClient):
    """
    Implementation of a geocoding client using the SmartyStreets API.
    Requires an authorization ID as well as an authentication token
    in order to build a street lookup client.
    """

    def __init__(self, auth_id, auth_token):
        self.auth_id = auth_id
        self.auth_token = auth_token
        creds = StaticCredentials(auth_id, auth_token)
        self.__client = (
            ClientBuilder(creds)
            .with_licenses(["us-standard-cloud"])
            .build_us_street_api_client()
        )

    @property
    def client(self) -> us_street.Client:
        return self.__client

    def geocode_from_str(self, address: str) -> Union[GeocodeResult, None]:
        """
        Geocodes a string-formatted address using SmartyStreets. If the result
        comes back valid, output is stored in a GeocodeResult object. If the
        result could not be latitude- or longitude-located, then Smarty failed
        to precisely geocode the address, so no result is returned.

        :param address: The address to geocode, given as a string
        """
        lookup = Lookup(street=address)
        self.__client.send_lookup(lookup)
        return _parse_smarty_result(lookup)

    def geocode_from_dict(self, address: dict) -> Union[GeocodeResult, None]:
        """
        Geocodes a dictionary-formatted address using SmartyStreets. The given
        dictionary should conform to standard nomenclature around address fields,
        including:

            street: the number and street address
            street2: additional street level information (if needed)
            apartment: apartment or suite number (if needed)
            city: city to geocode
            state: state to geocode
            zip: the postal code to use

        There is no minimum number of fields that must be specified to use this
        function; however, a minimum of street, city, and state are suggested
        for the best matches. If a result is found, it is encoded as a
        GeocodeResult object and returned, otherwise the function returns None.

        :param address: a dictionary with fields outlined above
        """

        # Configure the lookup with whatever provided address values
        # were in the user-given dictionary
        lookup = Lookup()
        lookup.street = address.get("street", "")
        lookup.street2 = address.get("street2", "")
        lookup.secondary = address.get("apartment", "")
        lookup.city = address.get("city", "")
        lookup.state = address.get("state", "")
        lookup.zipcode = address.get("zip", "")
        lookup.match = "strict"

        # Geocode and return
        self.__client.send_lookup(lookup)
        return _parse_smarty_result(lookup)


def _parse_smarty_result(lookup):
    """
    Private helper function to parse a returned Smarty geocoding result into
    our standardized GeocodeResult class.

    :param lookup: The us_street.lookup client instantiated for geocoding
    """
    # Valid responses have results with lat/long
    if lookup.result and lookup.result[0].metadata.latitude:
        smartystreets_result = lookup.result[0]
        street_address = [smartystreets_result.delivery_line_1]
        if smartystreets_result.delivery_line_2:
            street_address.append(smartystreets_result.delivery_line_2)

        # Format the Smarty result into our standard dataclass object
        return GeocodeResult(
            street=street_address,
            city=smartystreets_result.components.city_name,
            state=smartystreets_result.components.state_abbreviation,
            zipcode=smartystreets_result.components.zipcode,
            county_fips=smartystreets_result.metadata.county_fips,
            county_name=smartystreets_result.metadata.county_name,
            lat=smartystreets_result.metadata.latitude,
            lng=smartystreets_result.metadata.longitude,
            precision=smartystreets_result.metadata.precision,
        )

    return
