from typing import Union

from smartystreets_python_sdk import ClientBuilder
from smartystreets_python_sdk import StaticCredentials
from smartystreets_python_sdk import us_street
from smartystreets_python_sdk.us_street.lookup import Lookup

from phdi.geospatial.core import BaseGeocodeClient
from phdi.geospatial.core import GeocodeResult


class SmartyGeocodeClient(BaseGeocodeClient):
    """
    Represents a PHDI-supplied geocoding client using the Smarty API.
    Requires an authorization ID as well as an authentication token
    in order to build a street lookup client.
    """

    def __init__(
        self,
        smarty_auth_id: str,
        smarty_auth_token: str,
        licenses: list[str] = ["us-standard-cloud"],
    ):
        self.smarty_auth_id = smarty_auth_id
        self.smarty_auth_token = smarty_auth_token
        creds = StaticCredentials(smarty_auth_id, smarty_auth_token)
        self.__client = (
            ClientBuilder(creds).with_licenses(licenses).build_us_street_api_client()
        )

    @property
    def client(self) -> us_street.Client:
        """
        This property:
          1. defines a private instance variable __client
          2. makes it accessible through the use of .client()

        This property holds a Smarty-specific connection client that
        allows a user to geocode without directly referencing the
        underlying vendor service client.
        """
        return self.__client

    def geocode_from_str(self, address: str) -> Union[GeocodeResult, None]:
        """
        Geocodes the provided address, which is formatted as a string. If the
        result cannot be latitude- or longitude-located, then Smarty failed
        to precisely geocode the address, so no result is returned. Raises
        an error if the provided address is empty.

        :param address: The address to geocode, given as a string.
        :raises ValueError: When the address does not include street number and name.
        :return: A geocoded address (if valid result) or None (if no valid result).
        """

        # The smarty Lookup class will parse a BadRequestError but retry
        # 5 times if the lookup address is blank, so catch that here
        if address == "":
            raise ValueError("Address must include street number and name at a minimum")

        lookup = Lookup(street=address)
        self.__client.send_lookup(lookup)
        return self._parse_smarty_result(lookup)

    def geocode_from_dict(self, address: dict) -> Union[GeocodeResult, None]:
        """
        Geocodes the provided address, which is formatted as a dictionary.

        The given dictionary should conform to standard nomenclature around address
        fields, including:

        * `street`: the number and street address
        * `street2`: additional street level information (if needed)
        * `apartment`: apartment or suite number (if needed)
        * `city`: city to geocode
        * `state`: state to geocode
        * `postal_code`: the postal code to use
        * `urbanization`: urbanization code for area, sector, or regional
        * `development`: (only used for Puerto Rican addresses)

        There is no minimum number of fields that must be specified to use this
        function; however, a minimum of street, city, and state are suggested
        for the best matches.

        :param address: A dictionary with fields outlined above.
        :raises Exception: When the address street is an empty string.
        :return: A geocoded address (if valid result) or None (if no valid result).
        """

        # Smarty geocode requests must include a street level
        # field in the payload, otherwise generates BadRequestError
        if address.get("street", "") == "":
            raise ValueError("Address must include street number and name at a minimum")

        # Configure the lookup with whatever provided address values
        # were in the user-given dictionary
        lookup = Lookup()
        lookup.street = address.get("street", "")
        lookup.street2 = address.get("street2", "")
        lookup.secondary = address.get("apartment", "")
        lookup.city = address.get("city", "")
        lookup.state = address.get("state", "")
        lookup.zipcode = address.get("postal_code", "")
        lookup.urbanization = address.get("urbanization", "")
        lookup.match = "strict"

        self.__client.send_lookup(lookup)
        return self._parse_smarty_result(lookup)

    @staticmethod
    def _parse_smarty_result(lookup) -> Union[GeocodeResult, None]:
        """
        Parses a returned Smarty geocoding result into a GeocodeResult object.
        If the Smarty lookup is null or doesn't include latitude and longitude
        information, returns None instead.

        :param lookup: The us_street.lookup client instantiated for geocoding.
        :return: The geocoded address (if valid result) or None (if no valid result).
        """
        # Valid responses have results with lat/long
        if lookup.result and lookup.result[0].metadata.latitude:
            smartystreets_result = lookup.result[0]
            street_address = [smartystreets_result.delivery_line_1]
            if smartystreets_result.delivery_line_2:
                street_address.append(smartystreets_result.delivery_line_2)

            # Format the Smarty result into our standard dataclass object
            return GeocodeResult(
                line=street_address,
                city=smartystreets_result.components.city_name,
                state=smartystreets_result.components.state_abbreviation,
                postal_code=smartystreets_result.components.zipcode,
                county_fips=smartystreets_result.metadata.county_fips,
                county_name=smartystreets_result.metadata.county_name,
                lat=smartystreets_result.metadata.latitude,
                lng=smartystreets_result.metadata.longitude,
                precision=smartystreets_result.metadata.precision,
            )

        return
