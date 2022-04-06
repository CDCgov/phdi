import json
import pathlib
import pytest

from unittest import mock

from IntakePipeline.transform import find_patient_resources, transform_bundle

from phdi_transforms.geo import GeocodeResult


@pytest.fixture()
def combined_bundle():
    return json.load(
        open(pathlib.Path(__file__).parent / "assets" / "patient_bundle.json")
    )


def test_find_patient_record(combined_bundle):
    patients = find_patient_resources(combined_bundle)
    assert len(patients) == 1
    assert patients[0].get("resource").get("id") == "some-uuid"


@mock.patch("IntakePipeline.transform.geocode")
def test_transform_bundle(patched_geocode, combined_bundle):
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

    incoming = find_patient_resources(combined_bundle)[0]

    expected = {
        "resourceType": "Patient",
        "id": "some-uuid",
        "identifier": incoming.get("resource").get("identifier"),
        "name": [{"family": "DOE", "given": ["JOHN", "DANGER"], "use": "official"}],
        "telecom": [
            {"system": "phone", "use": "home"},
            {"system": "email", "value": "johndanger@doe.net"},
        ],
        "birthDate": "1983-02-01",
        "gender": "female",
        "address": [
            {
                "extension": [
                    {
                        "url": "http://hl7.org/fhir/StructureDefinition/geolocation",
                        "extension": [
                            {"url": "latitude", "valueDecimal": 45.123},
                            {"url": "longitude", "valueDecimal": -70.234},
                        ],
                    },
                ],
                "line": ["123 FAKE ST", "UNIT 3"],
                "city": "NEW YORK",
                "state": "NY",
                "postalCode": "10001",
                "country": "USA",
                "use": "home",
            }
        ],
    }

    transform_bundle(mock.Mock(), combined_bundle)
    assert combined_bundle.get("entry")[1].get("resource") == expected
    patched_geocode.assert_called()
