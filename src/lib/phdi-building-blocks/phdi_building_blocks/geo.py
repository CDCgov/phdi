from typing import List
from pydantic import BaseModel

from phdi_building_blocks.utils import find_patient_resources

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


def geocode_patient_address(bundle: dict, client: us_street.Client) -> dict:
    """Given a FHIR bundle and a SmartyStreets client, geocode all patient addresses
    in all patient resources in the bundle."""

    for resource in find_patient_resources(bundle):
        patient = resource.get("resource")
        if "extension" not in patient:
            patient["extension"] = []

        raw_addresses = []
        std_addresses = []
        for address in patient.get("address", []):
            # Generate a one-line address to pass to the geocoder
            one_line = " ".join(address.get("line", []))
            one_line += f" {address.get('city')}, {address.get('state')}"
            if "postalCode" in address and address["postalCode"]:
                one_line += f" {address['postalCode']}"
            raw_addresses.append(one_line)

            geocoded = geocode(client, one_line)
            std_one_line = ""
            if geocoded:
                address["line"] = geocoded.address
                address["city"] = geocoded.city
                address["state"] = geocoded.state
                address["postalCode"] = geocoded.zipcode
                std_one_line = f"{geocoded.address} {geocoded.city}, {geocoded.state} {geocoded.zipcode}"  # noqa
                std_addresses.append(std_one_line)

                if "extension" not in address:
                    address["extension"] = []

                address["extension"].append(
                    {
                        "url": "http://hl7.org/fhir/StructureDefinition/geolocation",
                        "extension": [
                            {"url": "latitude", "valueDecimal": geocoded.lat},
                            {"url": "longitude", "valueDecimal": geocoded.lng},
                        ],
                    }
                )
        any_dffs = (len(raw_addresses) != len(std_addresses)) or any(
            [raw_addresses[i] != std_addresses[i] for i in range(len(raw_addresses))]
        )
        patient["extension"].append(
            {
                "url": "http://usds.gov/fhir/phdi/StructureDefinition/address-was-standardized",  # noqa
                "valueBoolean": any_dffs,
            }
        )

    return bundle
