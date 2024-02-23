import copy

from smartystreets_python_sdk import us_street

from phdi.fhir.geospatial.core import BaseFhirGeocodeClient
from phdi.fhir.utils import get_one_line_address
from phdi.geospatial.smarty import SmartyGeocodeClient


class SmartyFhirGeocodeClient(BaseFhirGeocodeClient):
    """
    Implementation of a geocoding client designed to handle FHIR-
    formatted data using the SmartyStreets API.
    Requires an authorization ID as well as an authentication token
    in order to build a street lookup client.
    """

    def __init__(
        self,
        smarty_auth_id: str,
        smarty_auth_token: str,
        licenses: list[str] = ["us-standard-cloud"],
    ):
        self.__client = SmartyGeocodeClient(smarty_auth_id, smarty_auth_token, licenses)

    @property
    def geocode_client(self) -> us_street.Client:
        """
        An instance of the underlying Smarty client.
        Allows the FHIR wrapper to access a SmartyStreets-
        specific connection client without instantiating its own
        copy. Provides access to the respective `geocode_from_str`
        and `geocode_from_dict` methods if they're desired.
        """
        return self.__client

    def geocode_resource(self, resource: dict, overwrite=True) -> dict:
        """
        Performs geocoding on one or more addresses in a given FHIR
        resource and returns either the result or a copy thereof.
        Currently supported resource types are:

        * Patient

        :param resource: The resource whose addresses should be geocoded.
        :param overwrite: If true, `resource` is modified in-place;
          if false, a copy of `resource` modified and returned.  Default: `True`
        :return: The geocoded resource as a dict.
        """
        if not overwrite:
            resource = copy.deepcopy(resource)

        resource_type = resource.get("resourceType", "")
        if resource_type == "Patient":
            self._geocode_patient_resource(resource)

        return resource

    def _geocode_patient_resource(self, patient: dict) -> None:
        """
        Geocodes all addresses in a patient resource.

        :param patient: A FHIR Patient resource.
        """
        for address in patient.get("address", []):
            address_str = get_one_line_address(address)
            standardized_address = self.__client.geocode_from_str(address_str)

            # Update fields with new, standardized information
            if standardized_address:
                address["line"] = standardized_address.line
                address["city"] = standardized_address.city
                address["state"] = standardized_address.state
                address["county"] = standardized_address.county_name
                address["postalCode"] = standardized_address.postal_code
                self._store_lat_long_extension(
                    address, standardized_address.lat, standardized_address.lng
                )

    def geocode_bundle(self, bundle: dict, overwrite=True) -> dict:
        """
        Geocodes on all resources in a given FHIR bundle whose
        resource type is among those supported by the PHDI SDK. Currently,
        this includes:

        * Patient

        :param bundle: A bundle of FHIR resources.
        :param overwrite: If true, `bundle` is modified in-place;
          if false, a copy of `bundle` modified and returned.  Default: `True`
        :return: The FHIR bundle with geocoded address(es).
        """
        if not overwrite:
            bundle = copy.deepcopy(bundle)

        for entry in bundle.get("entry", []):
            _ = self.geocode_resource(entry.get("resource", {}), overwrite=True)

        return bundle
