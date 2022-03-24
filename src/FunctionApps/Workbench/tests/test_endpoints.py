from unittest import mock
from fastapi.testclient import TestClient

from Workbench.api import app
from phdi_transforms.geo import GeocodeResult


TEST_ENV = {"SMARTYSTREETS_AUTH_ID": "id", "SMARTYSTREETS_AUTH_TOKEN": "token"}
client = TestClient(app)


def test_standardize_name():
    assert client.get("/basic/name").status_code == 422

    resp = client.get("/basic/name?name=%20jOhN DoE")
    assert resp.status_code == 200
    assert resp.json() == {"value": "JOHN DOE"}


def test_standardize_phone():
    assert client.get("/basic/phone").status_code == 422

    resp = client.get("/basic/phone?phone=(215) 555-1212")
    assert resp.status_code == 200
    assert resp.json() == {"value": "2155551212"}


@mock.patch("Workbench.api.get_smartystreets_client")
@mock.patch("Workbench.api.geocode")
@mock.patch.dict("os.environ", TEST_ENV)
def test_geocode(patched_geocode, patched_get_client):
    assert client.get("/geo/address").status_code == 422

    patched_get_client.return_value = None
    patched_geocode.return_value = GeocodeResult(
        address=["123 Fake St"],
        city="Some City",
        state="NY",
        zipcode="10001",
        county_fips="12345",
        county_name="Somecounty",
        lat=123.45,
        lng=-101.0,
        precision="Zip9",
    )

    resp = client.get("/geo/address?address=some-address")
    assert resp.status_code == 200
    assert resp.json() == {
        "address": ["123 Fake St"],
        "city": "Some City",
        "state": "NY",
        "zipcode": "10001",
        "county_fips": "12345",
        "county_name": "Somecounty",
        "lat": 123.45,
        "lng": -101.0,
        "precision": "Zip9",
    }
