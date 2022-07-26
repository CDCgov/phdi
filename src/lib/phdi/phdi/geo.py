from phdi_building_blocks.utils import find_resource_by_type, get_one_line_address

from smartystreets_python_sdk import StaticCredentials, ClientBuilder
from smartystreets_python_sdk import us_street
from smartystreets_python_sdk.us_street.lookup import Lookup

from typing import List, Union
from pydantic import BaseModel
import copy


class GeocodeResult(BaseModel):
    """
    A basic abstract class representing a successful geocoding response.
    SmartyStreets asks us to implement a custom result to wrap their
    base model in for ease of working with.
    """

    address: List[str]
    city: str
    state: str
    zipcode: str
    county_fips: str
    county_name: str
    lat: float
    lng: float
    precision: str


def get_geocoder_result(
    address: str, client: us_street.Client
) -> Union[GeocodeResult, None]:
    """
    Given an API client and an address, attempt to call the smartystreets API
    and use our wrapper class to return a succinctly encapsulated result. If
    a valid result is found, it will be returned. Otherwise, the function
    returns None.

    :param address: The address to perform a geocoding lookup for
    :param client: the SmartyStreets API Client suitable for use with street addresses
    in the US
    """

    lookup = Lookup(street=address)
    client.send_lookup(lookup)

    # Valid responses have results with lat/long
    if lookup.result and lookup.result[0].metadata.latitude:
        smartystreets_result = lookup.result[0]
        street_address = [smartystreets_result.delivery_line_1]
        if smartystreets_result.delivery_line_2:
            street_address.append(smartystreets_result.delivery_line_2)

        return GeocodeResult(
            address=street_address,
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


def get_smartystreets_client(auth_id: str, auth_token: str) -> us_street.Client:
    """
    Build a smartystreets api client from an auth id and token.

    :param auth_id: Authentication ID to build the client with
    :param auth_token: The token that allows us to access the client
    """

    creds = StaticCredentials(auth_id, auth_token)
    return (
        ClientBuilder(creds)
        .with_licenses(["us-standard-cloud"])
        .build_us_street_api_client()
    )


# TODO Find a way to generalize this such that it's applicable to all resource types
def geocode_patients(
    bundle: dict,
    client: us_street.Client,
    overwrite: bool = True,
) -> dict:
    """
    Given a FHIR bundle and a SmartyStreets client, geocode all patient addresses
    across all patient resources in the bundle. If the overwrite parameter is
    false, the function makes a deep copy of the data before operating so that
    the source data is unchanged and the new standardized bundle may be passed
    by value to other building blocks.

    :param dict bundle: A FHIR resource bundle
    :param us_street.Client client: The smartystreets API client to geocode
        with
    :param overwrite: Whether to write the new standardizations directly
        into the given bundle, changing the original data (True is yes)
    """
    # Copy the data if we don't want to alter the original
    if not overwrite:
        bundle = copy.deepcopy(bundle)

    # Standardize each patient in turn
    for resource in find_resource_by_type(bundle, "Patient"):
        patient = resource.get("resource")
        geocode_and_parse_addresses_for_patient(patient, client)

    return bundle


def _geocode_and_parse_address(
    address: dict, client: us_street.Client
) -> GeocodeResult:
    """
    Helper function to perform geocoding on a single address from a patient
    resource. Here, the address is expressed in dictionary form, as it comes
    straight out of a FHIR bundle.

    :param address: A patient's address in FHIR / JSON
    :param client: The API client to geocode with
    """

    raw_one_line = get_one_line_address(address)
    geocoded_result = get_geocoder_result(raw_one_line, client)

    return geocoded_result


# TODO: Find a way to generalize this such that it's applicable to all resource types
def geocode_and_parse_addresses_for_patient(
    patient: dict, client: us_street.Client
) -> None:
    """
    Helper function to handle the parsing, standardizing, and geocoding of all addresses
    belonging to a single patient in a FHIR resource bundle.

    :param patient: A Patient resource FHIR profile
    :param client: The API client to geocode with
    """

    for address in patient.get("address", []):
        standardized_address = _geocode_and_parse_address(address, client)

        # Update fields with new, standardized information
        if standardized_address:
            address["line"] = standardized_address.address
            address["city"] = standardized_address.city
            address["state"] = standardized_address.state
            address["postalCode"] = standardized_address.zipcode

            # Need an extension to track lat/long
            if "extension" not in address:
                address["extension"] = []
            address["extension"].append(
                {
                    "url": "http://hl7.org/fhir/StructureDefinition/geolocation",
                    "extension": [
                        {
                            "url": "latitude",
                            "valueDecimal": standardized_address.lat,
                        },
                        {
                            "url": "longitude",
                            "valueDecimal": standardized_address.lng,
                        },
                    ],
                }
            )
