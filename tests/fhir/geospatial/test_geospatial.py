from phdi.fhir.geospatial import FhirGeocodeClient

import json
import pathlib


def test_get_one_line_address():
    bundle = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "patient_bundle.json"
        )
    )
    patient = bundle["entry"][1]["resource"]
    result_address = "123 Fake St Unit #F Faketon, NY 10001-0001"
    assert (
        FhirGeocodeClient._get_one_line_address(patient.get("address", [])[0])
        == result_address
    )


def test_store_lat_long():
    bundle = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "patient_bundle.json"
        )
    )
    patient = bundle["entry"][1]["resource"]
    address = patient.get("address", {})[0]
    FhirGeocodeClient._store_lat_long_extension(address, 40.032, -64.987)
    assert address["extension"] is not None

    stored_both = False
    for extension in address["extension"]:
        if "geolocation" in extension.get("url"):
            lat_dict = next(
                x for x in extension.get("extension") if x.get("url") == "latitude"
            )
            lng_dict = next(
                x for x in extension.get("extension") if x.get("url") == "longitude"
            )
            stored_both = (
                lat_dict.get("valueDecimal") == 40.032
                and lng_dict.get("valueDecimal") == -64.987
            )
    assert stored_both
