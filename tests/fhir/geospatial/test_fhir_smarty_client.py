import copy
import json
import pathlib
from unittest import mock

from phdi.fhir.geospatial.smarty import SmartyFhirGeocodeClient
from phdi.geospatial.core import GeocodeResult


def test_geocode_resource():
    smarty_auth_id = mock.Mock()
    smarty_auth_token = mock.Mock()
    smarty_client = SmartyFhirGeocodeClient(smarty_auth_id, smarty_auth_token)
    assert smarty_client.geocode_client is not None

    geocoded_response = GeocodeResult(
        line=["123 FAKE ST"],
        city="New York",
        state="NY",
        lat=45.123,
        lng=-70.234,
        county_fips="36061",
        county_name="New York",
        postal_code="10001",
        precision="Zip9",
    )

    bundle = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "general"
            / "patient_bundle.json"
        )
    )

    patient = bundle["entry"][1]["resource"]
    standardized_patient = copy.deepcopy(patient)
    address = standardized_patient["address"][0]
    address["line"] = geocoded_response.line
    address["city"] = geocoded_response.city
    address["state"] = geocoded_response.state
    address["county"] = geocoded_response.county_name
    address["postalCode"] = geocoded_response.postal_code
    address["extension"] = []
    address["extension"].append(
        {
            "url": "http://hl7.org/fhir/StructureDefinition/geolocation",
            "extension": [
                {"url": "latitude", "valueDecimal": geocoded_response.lat},
                {"url": "longitude", "valueDecimal": geocoded_response.lng},
            ],
        }
    )

    smarty_client.geocode_client.geocode_from_str = mock.Mock()
    smarty_client.geocode_client.geocode_from_str.return_value = geocoded_response

    # Case 1: Overwrite = False
    returned_patient = smarty_client.geocode_resource(patient, overwrite=False)
    assert standardized_patient == returned_patient
    assert returned_patient != patient

    # Case 2: Overwrite = True
    assert standardized_patient == smarty_client.geocode_resource(patient)
    smarty_client.geocode_client.geocode_from_str.assert_called()


def test_geocode_bundle():
    smarty_auth_id = mock.Mock()
    smarty_auth_token = mock.Mock()
    smarty_client = SmartyFhirGeocodeClient(smarty_auth_id, smarty_auth_token)
    assert smarty_client.geocode_client is not None

    geocoded_response = GeocodeResult(
        line=["123 FAKE ST"],
        city="New York",
        state="NY",
        lat=45.123,
        lng=-70.234,
        county_fips="36061",
        county_name="New York",
        postal_code="10001",
        precision="Zip9",
    )

    bundle = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "general"
            / "patient_bundle.json"
        )
    )
    standardized_bundle = copy.deepcopy(bundle)
    patient = standardized_bundle["entry"][1]["resource"]
    address = patient["address"][0]
    address["line"] = geocoded_response.line
    address["city"] = geocoded_response.city
    address["state"] = geocoded_response.state
    address["county"] = geocoded_response.county_name
    address["postalCode"] = geocoded_response.postal_code
    address["extension"] = []
    address["extension"].append(
        {
            "url": "http://hl7.org/fhir/StructureDefinition/geolocation",
            "extension": [
                {"url": "latitude", "valueDecimal": geocoded_response.lat},
                {"url": "longitude", "valueDecimal": geocoded_response.lng},
            ],
        }
    )

    smarty_client.geocode_client.geocode_from_str = mock.Mock()
    smarty_client.geocode_client.geocode_from_str.return_value = geocoded_response
    returned_bundle = smarty_client.geocode_bundle(bundle, overwrite=False)
    assert standardized_bundle == returned_bundle
    assert bundle != standardized_bundle
    smarty_client.geocode_client.geocode_from_str.assert_called()
