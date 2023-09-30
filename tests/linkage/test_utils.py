import json
import pathlib
from phdi.linkage.utils import (
    get_address_lines,
    get_geo_latitude,
    get_geo_longitude,
    get_patient_addresses,
    get_patient_ethnicity,
    get_patient_names,
    get_patient_race,
    get_settings,
)


patient_resource = json.load(
    open(
        pathlib.Path(__file__).parent.parent.parent
        / "tests"
        / "assets"
        / "general"
        / "patient_resource_w_extensions.json"
    )
)


def test_get_patient_ethnicity():
    patient_eth = get_patient_ethnicity(patient_resource)

    assert patient_eth == "Hispanic or Latino"


def test_get_patient_race():
    patient_eth = get_patient_race(patient_resource)

    assert patient_eth == "White"


def test_address_lines():
    address = {"address": get_patient_addresses(patient_resource)}
    lines = get_address_lines(address)

    assert len(lines) > 0


def test_geo_lat():
    address = {"address": get_patient_addresses(patient_resource)}
    lat = get_geo_latitude(address)
    assert lat == 34.58002


def test_geo_long():
    address = {"address": get_patient_addresses(patient_resource)}
    lon = get_geo_longitude(address)
    assert lon == -118.08925


def test_get_patient_names():
    names = get_patient_names(patient_resource)
    for name in names:
        assert name.get("family") == "doe"
        given_names = name.get("given")
        assert len(given_names) == 2
        assert given_names[0] == "John "
        assert given_names[1] == " Danger "
