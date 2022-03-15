from typing import TypedDict

from smartystreets_python_sdk import StaticCredentials, ClientBuilder
from smartystreets_python_sdk import us_street
from smartystreets_python_sdk.us_street.lookup import Lookup


class GeocodeResult(TypedDict):
    """
    A class representing a successful geocoding response
    """

    key: str
    address: str
    zipcode: str
    fips: str
    lat: float
    lng: float


def geocode(client: us_street.Client, address: str) -> GeocodeResult:
    """
    Given an API client and an address, attempt to call the smartystreets API
    """

    lookup = Lookup(street=address)
    client.send_lookup(lookup)

    if lookup.result:
        res = lookup.result[0]

        addr = [res.delivery_line_1]
        if res.delivery_line_2:
            addr.append(res.delivery_line_2)

        return {
            "address": addr,
            "city": res.components.city_name,
            "state": res.components.state_abbreviation,
            "zipcode": res.components.zipcode,
            "fips": res.metadata.county_fips,
            "lat": res.metadata.latitude,
            "lng": res.metadata.longitude,
        }


def get_smartystreets_client(auth_id: str, auth_token: str) -> us_street.Client:
    """
    Build a smartystreets api client from an auth id and token

    """

    creds = StaticCredentials(auth_id, auth_token)

    return (
        ClientBuilder(creds)
        .with_licenses(["us-standard-cloud"])
        .build_us_street_api_client()
    )
