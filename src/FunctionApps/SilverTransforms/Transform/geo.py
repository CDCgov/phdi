from typing import TypedDict

from smartystreets_python_sdk import StaticCredentials, ClientBuilder
from smartystreets_python_sdk import us_street
from smartystreets_python_sdk.us_street.lookup import Lookup


class GeocodeResult(TypedDict):
    address: str
    zipcode: str
    fips: str
    lat: float
    lng: float


def geocode(client: us_street.Client, address: str) -> GeocodeResult:
    lookup = Lookup(street=address)
    client.send_lookup(lookup)

    if lookup.result:
        res = lookup.result[0]

        # Put a space between address sections, if they exist
        addr = " ".join(
            part
            for part in [res.delivery_line_1, res.delivery_line_2, res.last_line]
            if part
        )

        return {
            "address": addr,
            "zipcode": res.components.zipcode,
            "fips": res.metadata.county_fips,
            "lat": res.metadata.latitude,
            "lng": res.metadata.longitude,
        }


def get_smartystreets_client(auth_id: str, auth_token: str) -> us_street.Client:
    creds = StaticCredentials(auth_id, auth_token)

    return (
        ClientBuilder(creds)
        .with_licenses(["us-standard-cloud"])
        .build_us_street_api_client()
    )
