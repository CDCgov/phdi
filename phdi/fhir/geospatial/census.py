import copy

from phdi.fhir.geospatial.core import BaseFhirGeocodeClient
from phdi.geospatial.census import CensusGeocodeClient


class CensusFhirGeocodeClient(BaseFhirGeocodeClient):
    """
    Implementation of a geocoding client designed to handle FHIR-
    formatted data using the Census API.
    """

    def __init__(self):
        self.__client = CensusGeocodeClient()

    def geocode_resource(self, resource: dict, overwrite=True) -> dict:
        """
        Performs geocoding on one or more addresses in a given FHIR
        resource and returns either the result or a copy thereof. The original street
        name, number, and any secondary address line information are returned in the
        original form.
        Currently supported resource types are:

            - Patient

        :param resource: The resource whose addresses should be geocoded.
        :param overwrite: Whether to save the geocoding information over
          the raw data, or to create a copy of the given data and write
          over that instead. Defaults to True (write over given data).
        :return: Geocoded resource as a dict.
        """
        # TODO: research additional APIs that return Apt (and other 2nd line addresses)
        # so that address.line can be overwritten
        if not overwrite:
            resource = copy.deepcopy(resource)

        resource_type = resource.get("resourceType", "")
        if resource_type == "Patient":
            self._geocode_patient_resource(resource)

        return resource

    def _geocode_patient_resource(self, patient: dict) -> None:
        """
        Handles geocoding of all addresses in a given patient resource.
        :param patient: The patient resource whose addresses should be geocoded.
        """
        for address in patient.get("address", []):
            address["street"] = " ".join(item for item in address["line"])
            standardized_address = self.__client.geocode_from_dict(address)

            # Update fields with new, standardized information
            if standardized_address:
                address["city"] = standardized_address.city
                address["state"] = standardized_address.state
                address["postalCode"] = standardized_address.postal_code
                self._store_lat_long_extension(
                    address, standardized_address.lat, standardized_address.lng
                )
                self._store_census_tract_extension(
                    address, standardized_address.census_tract
                )

                # Remove dict entry needed only for geocode_from_dict()
                del address["street"]

    def geocode_bundle(self, bundle: dict, overwrite=True) -> dict:
        """
        Performs geocoding on all resources in a given FHIR bundle whose
        resource type is among those supported by the PHDI SDK. Currently,
        this includes:

            - Patient

        :param bundle: A bundle of fhir resources.
        :param overwrite: Whether to overwrite the address data in the given
          bundle's resources (True), or whether to create a copy of the bundle
          and overwrite that instead (False). Defaults to True.
        :return: A FHIR bundle with geocoded address(es).
        """
        if not overwrite:
            bundle = copy.deepcopy(bundle)

        for entry in bundle.get("entry", []):
            self.geocode_resource(entry.get("resource", {}), overwrite=True)

        return bundle
