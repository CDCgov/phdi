from unittest import mock

from Transform.transforms import transform_record


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
