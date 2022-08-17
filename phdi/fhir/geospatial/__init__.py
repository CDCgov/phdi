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
