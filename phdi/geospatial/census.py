from typing import Union

from phdi.geospatial.core import BaseGeocodeClient, GeocodeResult
from phdi.transport import http_request_with_retry
import requests


class CensusGeocodeClient(BaseGeocodeClient):
    """
    Implementation of a geocoding client using the Census API.
    """

    def __init__(self):
        self.__client = ()

    def geocode_from_str(self, address: str) -> Union[GeocodeResult, None]:
        """
        Geocode a string-formatted address using Census API with searchtype =
        "onelineaddress". If a result is found, encode as a GeocodeResult object and
        return, otherwise the return None.

        :param address: The address to geocode, given as a string
        :param searchtype: onelineaddress OR address # doesn't yet support coordinates
        :return: A GeocodeResult object (if valid result) or None (if no valid
          result)
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
        Geocode a dictionary-formatted address using the Census API with searchtype =
        "address". If a result is found, encode as a GeocodeResult object and return,
        otherwise the return None.

        :param address: a dictionary with fields outlined above
        :return: A GeocodeResult object (if valid result) or None (if no valid
          result)
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
    def _format_address(address: Union[str, dict], searchtype: str):
        """
        Format address for Census API call according to address type.
        :param address: The address to geocode, given as a string
        :param searchtype: onelineaddress OR address
        :return: A properly formatted address for the Census API call, given as a
            string
        """
        # Check that the address contains structure number and street name # Finish
        if searchtype == "onelineaddress":
            address = address.replace(" ", "+").replace(",", "%2C")
            return f"onelineaddress?address={address}"
        elif searchtype == "address" and type(address) == dict:
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

        else:
            raise ValueError(
                "Cannot geocode given address. Provide city, state, and/or zip code"
            )

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
            is desired for the geoLookup (only needed when returntype = geographies)
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
        Call the Census endpoint with a given URL using the http_request_with_retry
        method.

        :param url: A URL for the Census API request, as a string
        :return: A response from queried endpoint
        :raises requests.HTTPError: If an unexpected status code is returned
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

        if response.status_code < 400:
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
                    item.strip()
                    for item in lookup["addressMatches"][0]["matchedAddress"].split(",")
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
