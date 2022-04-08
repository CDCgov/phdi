from typing import List
from pydantic import BaseModel

from smartystreets_python_sdk import StaticCredentials, ClientBuilder
from smartystreets_python_sdk import us_street
from smartystreets_python_sdk.us_street.lookup import Lookup


class GeocodeResult(BaseModel):
    """
    A class representing a successful geocoding response
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


def geocode(client: us_street.Client, address: str) -> GeocodeResult:
    """
    Given an API client and an address, attempt to call the smartystreets API
    """

    lookup = Lookup(street=address)
    client.send_lookup(lookup)

    if lookup.result and lookup.result[0].metadata.latitude:
        res = lookup.result[0]
        addr = [res.delivery_line_1]
        if res.delivery_line_2:
            addr.append(res.delivery_line_2)

        return GeocodeResult(
            address=addr,
            city=res.components.city_name,
            state=res.components.state_abbreviation,
            zipcode=res.components.zipcode,
            county_fips=res.metadata.county_fips,
            county_name=res.metadata.county_name,
            lat=res.metadata.latitude,
            lng=res.metadata.longitude,
            precision=res.metadata.precision,
        )


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
