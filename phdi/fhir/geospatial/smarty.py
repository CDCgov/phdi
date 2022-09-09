from typing import List
from copy import copy
from smartystreets_python_sdk import us_street

from phdi.geospatial.smarty import SmartyGeocodeClient
from phdi.fhir.geospatial.core import BaseFhirGeocodeClient
from phdi.fhir.utils import get_one_line_address


class SmartyFhirGeocodeClient(BaseFhirGeocodeClient):
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
        """
        This property:
          1. defines a private instance variable __client
          2. makes it accessible through the use of .client()

        This property holds an instance of the base SmartyGeocodeClient,
        which allows the FHIR wrapper to access a SmartyStreets-
        specific connection client without instantiating its own
        copy. It also provides access to the respective geocode_from_str
        and geocode_from_dict methods if they're desired.
        """
        return self.__client

    def geocode_resource(self, resource: dict, overwrite=True) -> dict:
        """
        Performs geocoding on one or more addresses in a given FHIR
        resource and returns either the result or a copy thereof.
        Currently supported resource types are:

            - Patient

        :param resource: The resource whose addresses should be geocoded
        :param overwrite: Whether to save the geocoding information over
          the raw data, or to create a copy of the given data and write
          over that instead. Defaults to True (write over given data).
        :param return: Geocoded address(es)
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
            address_str = get_one_line_address(address)
            standardized_address = self.__client.geocode_from_str(address_str)

            # Update fields with new, standardized information
            if standardized_address:
                address["line"] = standardized_address.line
                address["city"] = standardized_address.city
                address["state"] = standardized_address.state
                address["postalCode"] = standardized_address.postal_code
                self._store_lat_long_extension(
                    address, standardized_address.lat, standardized_address.lng
                )

    def geocode_bundle(self, bundle: List[dict], overwrite=True) -> List[dict]:
        """
        Perform geocoding on all resources in a given FHIR bundle whose
        resource type is among those supported by the PHDI SDK. Currently,
        this includes:

            - Patient

        :param bundle: A bundle of fhir resources
        :param overwrite: Whether to overwrite the address data in the given
          bundle's resources (True), or whether to create a copy of the bundle
          and overwrite that instead (False). Defaults to True
        :param return: A FHIR bundle with geocoded address(es)
        """
        if not overwrite:
            bundle = copy.deepcopy(bundle)

        for entry in bundle.get("entry", []):
            _ = self.geocode_resource(entry.get("resource", {}), overwrite=True)

        return bundle
