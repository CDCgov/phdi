import pytest
from unittest import mock

import json
import pathlib

from phdi_transforms.geo import GeocodeResult

from IntakePipeline.transform import transform_bundle


@pytest.fixture()
def bundle():
    return json.load(
        open(pathlib.Path(__file__).parent / "assets" / "patient_bundle.json")
    )


@mock.patch("IntakePipeline.transform.geocode")
def test_add_extensions_to_patient(patched_geocode, bundle):
    patched_geocode.return_value = GeocodeResult(
        key="123 Fake St New York, NY 10001",
        address=["123 FAKE ST", "UNIT 3"],
        city="NEW YORK",
        state="NY",
        zipcode="10001",
        fips="36061",
        lat=45.123,
        lng=-70.234,
        county_fips="dunno",
        county_name="no idea",
        precision="close-ish",
    )

    expected_extensions = [
        {
            "url": "http://usds.gov/fhir/phdi/StructureDefinition/family-name-was-standardized",  # noqa
            "valueBoolean": False,
        },
        {
            "url": "http://usds.gov/fhir/phdi/StructureDefinition/given-name-was-standardized",  # noqa
            "valueBoolean": True,
        },
        {
            "url": "http://usds.gov/fhir/phdi/StructureDefinition/phone-was-standardized",  # noqa
            "valueBoolean": True,
        },
        {
            "url": "http://usds.gov/fhir/phdi/StructureDefinition/address-was-standardized",  # noqa
            "valueBoolean": True,
        },
    ]

    transform_bundle(mock.Mock(), bundle)
    assert (
        bundle.get("entry")[1].get("resource").get("extension") == expected_extensions
    )
