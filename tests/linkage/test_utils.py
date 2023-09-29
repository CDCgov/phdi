import json
import pathlib
from phdi.linkage.utils import (
    get_address_lines,
    get_patient_addresses,
    get_patient_ethnicity,
    get_patient_race,
    get_settings,
)


patient_resource = json.load(
    open(
        pathlib.Path(__file__).parent.parent.parent
        / "tests"
        / "assets"
        / "general"
        / "patient_bundle_w_extensions.json"
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
