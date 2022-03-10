from unittest import mock

from Transform.transforms import transform_name
from Transform.transforms import transform_phone
from Transform.transforms import transform_record


def test_transform_name():
    assert "JOHN DOE" == transform_name(" JOHN DOE ")
    assert "JOHN DOE" == transform_name(" John Doe3 ")


def test_transform_phone():
    assert "0123456789" == transform_phone("0123456789")
    assert "0123456789" == transform_phone("(012)345-6789")
    assert transform_phone("345-6789") is None


@mock.patch("Transform.transforms.cached_geocode")
def test_transform_record(patched_geocode):
    patched_geocode.return_value = {
        "key": "123 Fake St New York, NY 10001",
        "address": ["123 FAKE ST", "UNIT 3"],
        "city": "NEW YORK",
        "state": "NY",
        "zipcode": "10001",
        "fips": "36061",
        "lat": 45.123,
        "lng": -70.234,
    }

    incoming = {
        "id": "some-uuid-that-shouldnt-be-touched",
        "name": [{"family": "Smith", "given": [" Jane", "Doe"]}],
        "telecom": [{"value": "(215) 555-1212"}],
        "address": [
            {
                "line": ["123 Fake St", "Unit 3"],
                "city": "New York",
                "state": "New York",
            }
        ],
    }

    expected = {
        "id": "some-uuid-that-shouldnt-be-touched",
        "name": [{"family": "SMITH", "given": ["JANE", "DOE"]}],
        "telecom": [{"value": "2155551212"}],
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
            }
        ],
    }

    assert expected == transform_record(mock.Mock(), mock.Mock(), incoming)
    patched_geocode.assert_called()
