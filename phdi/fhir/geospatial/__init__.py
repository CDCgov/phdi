from abc import ABC, abstractmethod
from typing import List


class FhirGeocodeClient(ABC):
    """
    A basic abstract class representing a vendor-agnostic geocoder client
    designed as a wrapper to process FHIR-based data (including resources
    and bundles). Requires implementing classes to define methods to
    geocode from both bundles and resources. Callers should use the
    provided interface functions (e.g. geocode_resource) to interact with
    the underlying vendor-specific client property.
    """

    @property
    @abstractmethod
    def geocode_client(self):
        """
        Since abstract base classes in python don't conventionally define
        instance variables (because they lack constructors), this abstract
        property does the following for implementing classes:
          1. defines a private instance variable __geocode_client to hold
             the base vendor-specific client; this client will be accessible
             in implementing functions
          2. makes it accessible through the use of .geocode_client()
        This instance variable will hold whatever vendor-specific client
        is instantiated by implementing classes so that they can perform
        geocoding without referencing the underlying client that connects
        to the vendor service.
        """
        pass

    @abstractmethod
    def geocode_resource(self, resource: dict) -> dict:
        """
        Function that uses the implementing client to perform geocoding
        on the provided resource, which is passed in as a dictionary.
        """
        pass

    @abstractmethod
    def geocode_bundle(self, bundle: List[dict]):
        """
        Function that uses the implementing client to perform geocoding
        on all supported resources in the provided FHIR bundle, which
        is passed in as a list of FHIR-formatted dictionaries.
        """
        pass

    @staticmethod
    def _get_one_line_address(address: dict) -> str:
        """
        Extract a one-line string representation of an address from a
        FHIR-formatted dictionary holding address information.

        :param address: The dictionary containing address fields
        :return: A string representation of the address contained in the
        FHIR dictionary, formatted for use with string-input geocoders
        """
        raw_one_line = " ".join(address.get("line", []))
        raw_one_line += f" {address.get('city')}, {address.get('state')}"
        if "postalCode" in address and address["postalCode"]:
            raw_one_line += f" {address['postalCode']}"
        return raw_one_line

    @staticmethod
    def _store_lat_long_extension(address: dict, lat: float, long: float) -> None:
        """
        Given a FHIR-formatted dictionary holding address fields, add
        appropriate extension data for latitude and longitude, if the fields
        aren't already present.

        :param address: A FHIR formatted dictionary holding address fields
        :param lat: The latitude to add to the FHIR data as an extension
        :param long: The longitude to add to the FHIR data as an extension
        :return: None, but leaves the given dictionary with an "extension"
        property if one is not already present, in which lat and long
        occur as FHIR-classified geolocation elements
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
