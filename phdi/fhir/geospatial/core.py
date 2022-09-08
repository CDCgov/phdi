from abc import ABC, abstractmethod
from typing import List


class BaseFhirGeocodeClient(ABC):
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
        pass  # pragma: no cover

    @abstractmethod
    def geocode_bundle(self, bundle: List[dict]):
        """
        Function that uses the implementing client to perform geocoding
        on all supported resources in the provided FHIR bundle, which
        is passed in as a list of FHIR-formatted dictionaries.
        """
        pass  # pragma: no cover

    @staticmethod
    def _store_lat_long_extension(address: dict, lat: float, long: float) -> None:
        """
        Given a FHIR-formatted dictionary holding address fields, add
        appropriate extension data for latitude and longitude, if the fields
        aren't already present. The extension data is added directly to the
        input dictionary, leaving lat and long as FHIR-identified
        geolocation elements.

        :param address: A FHIR formatted dictionary holding address fields
        :param lat: The latitude to add to the FHIR data as an extension
        :param long: The longitude to add to the FHIR data as an extension
        """
        if "extension" not in address:
            address["extension"] = []

        # Append with a properly resolving URL for FHIR's canonical geospatial
        # structure definition, as all extensions are required to have this
        # attribute; see https://www.hl7.org/fhir/extensibility.html
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
