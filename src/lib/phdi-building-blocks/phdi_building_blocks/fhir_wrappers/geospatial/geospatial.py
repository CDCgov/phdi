from abc import ABC, abstractmethod


class FhirGeocodeClient(ABC):
    """
    A basic abstract class representing a vendor-agnostic geocoder client
    designed as a wrapper to process FHIR-based data (including resources
    and bundles). Requires implementing classes to define methods to
    geocode from both bundles and resources. Treats the underlying client
    in vendor-specific implementations as a special internal property
    which can be accessed using .client().
    """

    @property
    @abstractmethod
    def client(self):
        pass

    @abstractmethod
    def geocode_resource(self):
        pass

    @abstractmethod
    def geocode_bundle(self):
        pass


def _get_one_line_address(address: dict) -> str:
    """
    Extract a one-line string representation of an address from a
    FHIR-formatted dictionary holding address information.

    :param address: The dictionary containing address fields
    """
    raw_one_line = " ".join(address.get("line", []))
    raw_one_line += f" {address.get('city')}, {address.get('state')}"
    if "postalCode" in address and address["postalCode"]:
        raw_one_line += f" {address['postalCode']}"
    return raw_one_line


def _store_lat_long_extension(address: dict, lat: float, long: float) -> None:
    """
    Given a FHIR-formatted dictionary holding address fields, add
    appropriate extension data for latitude and longitude, if the fields
    aren't already present.
    """
    if "extension" not in address:
        address["extension"] = []
    address["extension"].append(
        {
            "url": "http://hl7.org/fhir/StructureDefinition/geolocation",
            "extension": [
                {
                    "url": "latitude",
                    "valueDecimal": lat,
                },
                {
                    "url": "longitude",
                    "valueDecimal": long,
                },
            ],
        }
    )
