from phdi_building_blocks.geospatial.smarty import _parse_smarty_result
from phdi_building_blocks.fhir_wrappers.geospatial.geospatial import (
    FhirGeocodeClient,
    _get_one_line_address,
    _store_lat_long_extension,
)

from smartystreets_python_sdk import StaticCredentials, ClientBuilder
from smartystreets_python_sdk import us_street
from smartystreets_python_sdk.us_street.lookup import Lookup

from typing import List
from copy import copy


class SmartyGeocodeClient(FhirGeocodeClient):
    """
    Implementation of a geocoding client designed to handle FHIR-
    formatted data using the SmartyStreets API.
    Requires an authorization ID as well as an authentication token
    in order to build a street lookup client.
    """

    def __init__(self, auth_id, auth_token):
        self.auth_id = auth_id
        self.auth_token = auth_token
        creds = StaticCredentials(auth_id, auth_token)
        self.__client = (
            ClientBuilder(creds)
            .with_licenses(["us-standard-cloud"])
            .build_us_street_api_client()
        )

    @property
    def client(self) -> us_street.Client:
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
        """
        if not overwrite:
            resource = copy.deepcopy(resource)

        rtype = resource.get("resourceType", "")
        if rtype == "Patient":
            self._geocode_patient_resource(resource)

        return resource

    def _geocode_patient_resource(self, patient: dict) -> None:
        """
        Private helper function to handle geocoding of all addresses in
        a given patient resource.
        """
        for address in patient.get("address", []):
            address_str = _get_one_line_address(address)
            lookup = Lookup(street=address_str)
            self.__client.send_lookup(lookup)
            standardized_address = _parse_smarty_result(lookup)

            # Update fields with new, standardized information
            if standardized_address:
                address["line"] = standardized_address.street
                address["city"] = standardized_address.city
                address["state"] = standardized_address.state
                address["postalCode"] = standardized_address.zipcode
                _store_lat_long_extension(
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
        """
        if not overwrite:
            bundle = copy.deepcopy(bundle)

        for resource in bundle:
            _ = self.geocode_resource(resource, overwrite=True)

        return bundle
