from typing import Union
import requests


from phdi.geospatial.core import BaseGeocodeClient, GeocodeResult


class CensusGeocodeClient(BaseGeocodeClient):
    """
    Implementation of a geocoding client using the Census API.
    Requires an authorization ID as well as an authentication token
    in order to build a street lookup client.
    """

    def __init__(self):
        self.__client = ()

    # @property
    # def client(self) -> us_street.Client:
    #     """
    #     This property:
    #       1. defines a private instance variable __client
    #       2. makes it accessible through the use of .client()

    #     This property holds a SmartyStreets-specific connection client
    #     allows a user to geocode without directly referencing the
    #     underlying vendor service client.
    #     """
    #     return self.__client

    def geocode_from_str(self, address: str) -> Union[GeocodeResult, None]:
        """
        Geocode a string-formatted address using Census API. If the result
        comes back valid, output is stored in a GeocodeResult object.

        :param address: The address to geocode, given as a string
        :param searchtype: onelineaddress OR address # doesn't yet support coordinates
        :return: A GeocodeResult object (if valid result) or None (if no valid
          result)
        """
        formatted_address = self._format_address(address, searchtype="onelineaddress")
        url = self._get_url(formatted_address)
        response = self._call_census_api(url)
        parsed_response = self._parse_census_result(response)
        return parsed_response["matchedAddress"]

    # def geocode_from_dict(self, address: dict) -> Union[GeocodeResult, None]:
    #     """
    #     Geocode a dictionary-formatted address using SmartyStreets.
    #     If a result is found, encode as a GeocodeResult object and
    #     return, otherwise the return None.

    #     :param address: a dictionary with fields outlined above
    #     :return: A GeocodeResult object (if valid result) or None (if no valid
    #       result)
    #     """

    #     # Smarty geocode requests must include a street level
    #     # field in the payload, otherwise generates BadRequestError
    #     if address.get("street", "") == "":
    #         raise Exception("Must include street information at a minimum")

    #     # Configure the lookup with whatever provided address values
    #     # were in the user-given dictionary
    #     lookup = Lookup()
    #     lookup.street = address.get("street", "")
    #     lookup.street2 = address.get("street2", "")
    #     lookup.secondary = address.get("apartment", "")
    #     lookup.city = address.get("city", "")
    #     lookup.state = address.get("state", "")
    #     lookup.zipcode = address.get("postal_code", "")
    #     lookup.urbanization = address.get("urbanization", "")
    #     lookup.match = "strict"

    #     self.__client.send_lookup(lookup)
    #     return self._parse_smarty_result(lookup)

    @staticmethod
    def _format_address(address: Union[str, dict], searchtype: str):
        """
        Format address for Census API call according to address type.
        :param address: The address to geocode, given as a string
        :param searchtype: onelineaddress OR address OR coordinates; default is
            onelineaddress # Future consideration
        :return: A properly formatted address for the Census API call, given as a
            string
        """
        # Check that the address contains structure number and street name # Finish
        if address == "":
            raise Exception("Cannot geocode without street number and name")
        if searchtype == "onelineaddress":
            address = address.replace(" ", "+").replace(",", "%2C")
            return f"onelineaddress?address={address}"
        elif searchtype == "address" and type(address) == dict:
            return f"address?{address}"  # do we have an example of what the dict would
            # look like for an address given as a dict?
        else:
            raise Exception("Cannot geocode given address")

    @staticmethod
    def _get_url(address: str):
        """
        Get URL for Census API given inputs.
        :param address: The formatted address to geocode, given as a string
        :param returntype: locations (to get just geocoding response) or geographies
            (to get geocoding response as well as geoLookup) # Future consideration
        :param benchmark: A numerical ID or name that references what version of the
            locator should be searched. # Future consideration
        :param vintage: A numerical ID or name that references what vintage of geography
            is desired for the geoLookup (only needed when returntype = geographies).
            # Future consideration
        :param format: The format to be used for returning the standardized output
            (json, html) # Future consideration
        :param layers: By default, State, County, Tract, and Block layers are displayed
            when “geographies” is the chosen returntype. If additional or different
            layers are desired, they can be specified in a comma delimited list by ID
            or name

        :return: A URL for the Census API request, as a string
        """
        url = (
            f"https://geocoding.geo.census.gov/geocoder/geographies/{address}"
            + "&benchmark=Public_AR_Census2020"
            + "&vintage=Census2020_Census2020"
            + "&layers=[10]"
            + "&format=json"
        )
        return url

    @staticmethod
    def _call_census_api(url):
        """
        Call the Census endpoint with a given URL.

        :param url: A URL for the Census API request, as a string
        :return: A response from queried endpoint
        :raises requests.HTTPError: If an unexpected status code is returned
        """
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()["result"]
        else:
            raise requests.HTTPError(response=response)

    @staticmethod
    def _parse_census_result(lookup) -> Union[GeocodeResult, None]:
        """
        Private helper function to parse a returned Census geocoding result into
        our standardized GeocodeResult class. If the Census lookup is null or doesn't
        include matched address information, returns None instead.

        :param response: The Census API client instantiated for geocoding
        :return: A parsed GeocodeResult object (if valid result) or None (if
          no valid result)
        """
        if lookup is not None and lookup["addressMatches"] is not None:
            addressComponents = lookup["addressMatches"][0]["addressComponents"]
            blockComponents = lookup["addressMatches"][0]["geographies"][
                "Census Blocks"
            ][0]
            tractComponents = lookup["addressMatches"][0]["geographies"][
                "Census Tracts"
            ][0]
            countyComponents = lookup["addressMatches"][0]["geographies"]["Counties"][0]
            coordinateComponents = lookup["addressMatches"][0]["coordinates"]

            # Format the Census result into our standard dataclass object
            return GeocodeResult(
                line=[
                    item.strip()
                    for item in lookup["addressMatches"][0]["matchedAddress"].split(",")
                ],
                city=addressComponents["city"],
                state=addressComponents["state"],
                postal_code=addressComponents["zip"],
                county_fips=blockComponents["STATE"] + blockComponents["COUNTY"],
                county_name=countyComponents["BASENAME"],
                lat=coordinateComponents["y"],
                lng=coordinateComponents["x"],
                precision="zip5",  # I believe this will always be zip5 with layer 10
                geoid=blockComponents["GEOID"],
                census_tract=tractComponents["BASENAME"],
                census_block=blockComponents["BASENAME"],
            )


# # # ## SCRATCH
# address = "239 Greene Street, New York, NY, 10003"
# formatted_address = _format_address(address)
# url = _get_url(formatted_address)
# lookup = _call_census_api(url)
