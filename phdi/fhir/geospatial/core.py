from abc import ABC
from abc import abstractmethod


class BaseFhirGeocodeClient(ABC):
    """
    Represents a vendor-agnostic geocoder client designed to process
    FHIR-based data. Implementing classes should define methods to
    geocode from both bundles and resources. Callers should use the
    provided interface functions (e.g., geocode_resource) to interact with
    the underlying vendor-specific client property.
    """

    @abstractmethod
    def geocode_resource(self, resource: dict, overwrite=True) -> dict:
        """
        Performs geocoding, using the implementing client, on the provided resource,
        which is passed in as a dictionary.

        :param resource: A FHIR resource to be geocoded.
        :param overwrite: If true, `resource` is modified in-place;
          if false, a copy of `resource` modified and returned.  Default: `True`
        :return: The geocoded resource as a dict.
        """
        pass  # pragma: no cover

    @abstractmethod
    def geocode_bundle(self, bundle: dict, overwrite=True) -> dict:
        """
        Performs geocoding, using the implementing client, on all supported resources in
        the provided FHIR bundle which is passed in as a dictionary.

        :param bundle: A bundle of FHIR resources.
        :param overwrite: If true, `bundle` is modified in-place;
          if false, a copy of `bundle` modified and returned.  Default: `True`
        :return: The geocoded FHIR bundle as a dict.
        """
        pass  # pragma: no cover

    @staticmethod
    def _store_lat_long_extension(address: dict, lat: float, long: float) -> None:
        """
        Adds extension data for latitude and longitude, if the fields aren't already
        present, to a given FHIR-formatted dictionary holding address fields.
        The latitude and longitude data is added directly to the input dictionary.

        :param address: A FHIR formatted dictionary holding address fields.
        :param lat: The latitude to add to the FHIR data as an extension.
        :param long: The longitude to add to the FHIR data as an extension.
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

    @staticmethod
    def _store_census_tract_extension(address: dict, census_tract: str) -> None:
        """
        Adds appropriate extension data for census tract for each element in an address
        line, if the field isn't already present, to a given FHIR-formatted dictionary
        holding address fields. Add the extension data directly to the input dictionary,
        leaving census tract as a FHIR-identified geolocation element.

        :param address: A FHIR formatted dictionary holding address fields
        :param census_tract: The census tract to add to the FHIR data as an extension
        """

        # Append with a properly resolving URL for FHIR's canonical censusTract
        # structure definition, as all extensions are required to have this
        # attribute; see https://www.hl7.org/fhir/extensibility.html

        census_extension = {
            "url": "http://hl7.org/fhir/StructureDefinition/iso21090-ADXP-censusTract",
            "valueString": census_tract,
        }

        if address.get("_line") is None:
            address["_line"] = []
        for element_counter in range(len(address["line"])):
            try:
                address["_line"][element_counter].get("extension").append(
                    census_extension
                )
            except AttributeError:
                address["_line"][element_counter] = {"extension": []}
                address["_line"][element_counter].get("extension").append(
                    census_extension
                )
            except IndexError:
                address["_line"].append({"extension": [census_extension]})
