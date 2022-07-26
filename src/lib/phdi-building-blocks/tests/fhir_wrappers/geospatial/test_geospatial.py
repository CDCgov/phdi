import phdi_building_blocks.fhir.geospatial
import json
import pathlib


# def test_get_one_line_address():
#     bundle = json.load(
#         open(
#             pathlib.Path(__file__).parent.parent.parent
#             / "assets"
#             / "patient_bundle.json"
#         )
#     )
#     patient = bundle["entry"][1]["resource"]
#     result_address = "123 Fake St Unit #F Faketon, NY 10001-0001"
#     assert _get_one_line_address(patient.get("address", [])[0]) == result_address


# def test_store_lat_long():
#     pass
