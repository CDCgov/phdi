from phdi.geospatial.smarty import SmartyGeocodeClient
from phdi.fhir.geospatial import FhirGeocodeClient

from smartystreets_python_sdk import us_street

from typing import List
from copy import copy


class SmartyFhirGeocodeClient(FhirGeocodeClient):
    """
    Implementation of a geocoding client designed to handle FHIR-
    formatted data using the SmartyStreets API.
    Requires an authorization ID as well as an authentication token
    in order to build a street lookup client.
    """

    def __init__(self, auth_id, auth_token):
        self.__client = SmartyGeocodeClient(auth_id, auth_token)

    @property
    def geocode_client(self) -> us_street.Client:
        return self.__client

    def geocode_resource(self, resource: dict, overwrite=True) -> dict:
        """
        Performs geocoding on one or more addresses in a given FHIR
        resource. Currently supported resource types are:

            - Patient

        :param resource: The resource whose addresses should be geocoded
        :param overwrite: Whether to save the geocoding information over
          the raw data, or to create a copy of the given data and write
          over that instead. Defaults to True (write over given data).
        :return: The resource (or a copy thereof) with geocoded
          information added
        """
        if not overwrite:
            resource = copy.deepcopy(resource)

        resource_type = resource.get("resourceType", "")
        if resource_type == "Patient":
            self._geocode_patient_resource(resource)

        return resource

    def _geocode_patient_resource(self, patient: dict) -> None:
        """
        Private helper function to handle geocoding of all addresses in
        a given patient resource.
        """
        for address in patient.get("address", []):
            address_str = self._get_one_line_address(address)
            standardized_address = self.__client.geocode_from_str(address_str)

            # Update fields with new, standardized information
            if standardized_address:
                address["line"] = standardized_address.street
                address["city"] = standardized_address.city
                address["state"] = standardized_address.state
                address["postalCode"] = standardized_address.zipcode
                self._store_lat_long_extension(
                    address, standardized_address.lat, standardized_address.lng
                )

    def geocode_bundle(self, bundle: List[dict], overwrite=True) -> List[dict]:
        """
        Performs geocoding on all resources in a given FHIR bundle whose
        resource type is among those supported by the PHDI SDK. Currently,
        this includes:

            - Patient

        :param bundle: A bundle of fhir resources
        :param overwrite: Whether to overwrite the address data in the given
          bundle's resources (True), or whether to create a copy of the bundle
          and overwrite that instead (False). Defaults to True.
        :return: The given FHIR bundle (or a copy thereof) where all
          resources have updated geocoded information
        """
        if not overwrite:
            bundle = copy.deepcopy(bundle)

        for entry in bundle.get("entry", []):
            _ = self.geocode_resource(entry.get("resource", {}), overwrite=True)

        return bundle
