from typing import Literal
from typing import Union

import requests

from phdi.geospatial.core import BaseGeocodeClient
from phdi.geospatial.core import GeocodeResult
from phdi.transport import http_request_with_retry


class CensusGeocodeClient(BaseGeocodeClient):
    """
    Implementation of a geocoding client using the Census API.
    """

    def __init__(self):
        self.__client = ()

    def geocode_from_str(self, address: str) -> Union[GeocodeResult, None]:
        """
        Geocodes a string-formatted address using Census API with searchtype =
        "onelineaddress". If a result is found, encodes as a GeocodeResult object and
        return, otherwise the return None.

        :param address: The address to geocode, given as a string.
        :param searchtype: onelineaddress OR address # doesn't yet support coordinates.
        :raises ValueError: If address does not include street number and name.
        :return: A standardized address enriched with lat, lon, census tract, and more.
            Returns None if no valid result.
        """
        # Check for street num and name at minimum
        if address == "":
            raise ValueError("Address must include street number and name at a minimum")

        formatted_address = self._format_address(address, searchtype="onelineaddress")
        url = self._get_url(formatted_address)
        response = self._call_census_api(url)

        return self._parse_census_result(response)

    def geocode_from_dict(self, address: dict) -> Union[GeocodeResult, None]:
        """
        Geocodes the provided address, which is formatted as a dictionary.
        using the Census API with searchtype = "address". If a result is found, encodes
        as a GeocodeResult object and return, otherwise returns None.

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

        Street must be included to use this function; however, a minimum of street,
        city, and state are suggested for the best matches.

        :param address: A dictionary with fields outlined above.
        :raises ValueError: If address does not include street number and name.
        :return: A standardized address enriched with lat, lon, census tract, and more.
            Returns None if no valid result.
        """

        # Check for street num and name at minimum
        if address.get("street", "") == "":
            raise ValueError("Address must include street number and name at a minimum")

        # Configure the lookup with whatever provided address values
        # were in the user-given dictionary
        formatted_address = self._format_address(address, searchtype="address")
        url = self._get_url(formatted_address)
        response = self._call_census_api(url)

        return self._parse_census_result(response)

    @staticmethod
    def _format_address(
        address: Union[str, dict], searchtype: Literal["onelineaddress", "address"]
    ):
        """
        Formats an address for Census API call according to the given address type. A
        single line address, e.g, "100 5th Ave New York, NY" uses the "onelineaddress"
        searchtype while a dictionary formatted address uses the "address" searchtype.

        :param address: The address to geocode, given as a string or dictionary.
        :param searchtype: onelineaddress OR address.
        :raises ValueError: If address cannot be geocoded with specificity because it
            does not include city, state, and/or zipcode.
        :return: A properly formatted address for the Census API call, given as a
            string.
        """
        # Check that the address contains structure number and street name
        if searchtype == "onelineaddress":
            address = address.replace(" ", "+").replace(",", "%2C")
            return f"onelineaddress?address={address}"
        elif searchtype == "address" and isinstance(address, dict):
            street = address.get("street", "").replace(" ", "+").replace(",", "%2C")
            city = address.get("city", "").replace(" ", "+").replace(",", "%2C")
            state = address.get("state", "").replace(" ", "+").replace(",", "%2C")
            zip = address.get("zip", "").replace(" ", "+").replace(",", "%2C")

            # If only "street" is present, format address with
            # searchtype = "onelineaddress"
            if any(element != "" for element in [city, state, zip]):
                # Add non-empty elements
                formatted_address = f"address?street={street}"
                for element in [city, state, zip]:
                    if element == "":
                        continue
                    else:
                        if element == city:
                            formatted_address += f"&city={city}"
                        elif element == state:
                            formatted_address += f"&state={state}"
                        elif element == zip:
                            formatted_address += f"&zip={zip}"
                return formatted_address

            else:
                return f"onelineaddress?address={street}"

    @staticmethod
    def _get_url(address: str):
        """
        Gets URL for Census API given inputs.

        :param address: The formatted address to geocode, given as a string.
        :return: A URL for the Census API request, as a string.
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
        Calls the Census endpoint with a given URL using the http_request_with_retry
        method.

        :param url: A URL for the Census API request, as a string.
        :raises requests.HTTPError: If an unexpected status code is returned.
        :return: A response from queried endpoint.
        """
        http_url = url
        http_action = "GET"
        http_header = {"some-header": "some-header-value"}
        http_retry_count = 5

        response = http_request_with_retry(
            http_url,
            http_retry_count,
            http_action,
            [http_action],
            http_header,
        )

        if response.status_code != 200:
            raise requests.HTTPError(response=response)
        else:
            return response.json()["result"]

    @staticmethod
    def _parse_census_result(lookup) -> Union[GeocodeResult, None]:
        """
        Parses a returned Census geocoding result into our standardized GeocodeResult
        class. If the Census lookup is null or doesn't include matched address
        information, returns None instead.

        :param response: The Census API client instantiated for geocoding.
        :return: A parsed and standardized address enriched with lat, lon, census tract,
             and more. Returns None if no valid result.
        """

        if lookup is not None and lookup.get("addressMatches"):
            addressComponents = lookup.get("addressMatches", [{}])[0].get(
                "addressComponents", {}
            )
            blockComponents = (
                lookup.get("addressMatches", [{}])[0]
                .get("geographies", {})
                .get("Census Blocks", [None])[0]
            )
            tractComponents = (
                lookup.get("addressMatches", [{}])[0]
                .get("geographies", {})
                .get("Census Tracts", [None])[0]
            )
            countyComponents = (
                lookup.get("addressMatches", [{}])[0]
                .get("geographies", {})
                .get("Counties", [None])[0]
            )
            coordinateComponents = lookup.get("addressMatches", [{}])[0].get(
                "coordinates", {}
            )

            # Format the Census result into our standard dataclass object
            return GeocodeResult(
                line=[
                    lookup["addressMatches"][0]["matchedAddress"].split(",")[0].strip()
                ],
                city=addressComponents.get("city", ""),
                state=addressComponents.get("state", ""),
                postal_code=addressComponents.get("zip", ""),
                county_fips=blockComponents.get("STATE", "")
                + blockComponents.get("COUNTY", ""),
                county_name=countyComponents.get("BASENAME", ""),
                lat=coordinateComponents.get("y", None),
                lng=coordinateComponents.get("x", None),
                geoid=blockComponents.get("GEOID", ""),
                census_tract=tractComponents.get("BASENAME", ""),
                census_block=blockComponents.get("BASENAME", ""),
            )
