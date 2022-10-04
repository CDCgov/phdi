import json
import pathlib
import copy

from phdi.fhir.geospatial.census import CensusFhirGeocodeClient
from phdi.geospatial.core import GeocodeResult


def test_geocode_resource_census():
    census_client = CensusFhirGeocodeClient()
    assert census_client is not None

    geocoded_response = GeocodeResult(
        line=["239 Greene St", "Apt 4L"],
        city="NEW YORK",
        state="NY",
        lat=40.72962831414409,
        lng=-73.9954428687588,
        county_fips="36061",
        county_name="New York",
        postal_code="10003",
        census_tract="59",
    )

    bundle = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "patient_bundle_census.json"
        )
    )

    patient = bundle["entry"][1]["resource"]
    standardized_patient = copy.deepcopy(patient)
    address = standardized_patient["address"][0]
    address["city"] = geocoded_response.city
    address["state"] = geocoded_response.state
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
    address["_line"] = []
    address["_line"].append(
        {
            "extension": [
                {
                    "url": "http://hl7.org/fhir/StructureDefinition/"
                    + "iso21090-ADXP-censusTract",
                    "valueString": "59",
                }
            ]
        },
    )
    address["_line"].append(
        {
            "extension": [
                {
                    "url": "http://hl7.org/fhir/StructureDefinition/"
                    + "iso21090-ADXP-censusTract",
                    "valueString": "59",
                }
            ]
        },
    )

    # Case 1: Overwrite = False
    returned_patient = census_client.geocode_resource(patient, overwrite=False)
    assert standardized_patient == returned_patient
    assert returned_patient.get("address") != patient.get("address")
    assert returned_patient.get("address")[0].get("line") == ["239 Greene St", "Apt 4L"]

    # Case 2: Overwrite = True
    returned_patient = census_client.geocode_resource(patient, overwrite=True)
    print()
    print(f"Returned_patient:{returned_patient.get('address')}")
    print()
    print(f"standardized_patient:{standardized_patient.get('address')}")
    print()
    print(f"patient:{patient.get('address')}")
    print()
    assert returned_patient["address"][0].get("line") == [
        "239 Greene St",
        "Apt 4L",
    ]
    assert returned_patient == patient

    # Case 3: Patient already has an extension on line, and it's preserved.
    bundle = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "patient_bundle_census_extension.json"
        )
    )

    patient = bundle["entry"][1]["resource"]
    standardized_patient = copy.deepcopy(patient)

    # Case 3: Patient already has an extension on line, and it's preserved.
    # address["_line"] = []
    # address["_line"].append("None")
    # address["_line"].append({"extension": "existing_extensions"})
    # returned_patient = census_client.geocode_resource(patient, overwrite=True)
    # print()
    # print(f"Returned_patient:{returned_patient.get('address')}")
    # print()
    # print(f"standardized_patient:{standardized_patient.get('address')}")
    # print()


# def test_geocode_bundle_census():
#     census_client = CensusFhirGeocodeClient()
#     assert census_client is not None

#     geocoded_response = GeocodeResult(
#         line=["239 GREENE ST"],
#         city="NEW YORK",
#         state="NY",
#         lat=40.72962831414409,
#         lng=-73.9954428687588,
#         county_fips="36061",
#         county_name="New York",
#         postal_code="10003",
#         census_tract="59",
#     )

#     bundle = json.load(
#         open(
#             pathlib.Path(__file__).parent.parent.parent
#             / "assets"
#             / "patient_bundle_census.json"
#         )
#     )
#     standardized_bundle = copy.deepcopy(bundle)
#     patient = standardized_bundle["entry"][1]["resource"]
#     address = patient["address"][0]
#     address["line"] = geocoded_response.line
#     address["city"] = geocoded_response.city
#     address["state"] = geocoded_response.state
#     address["postalCode"] = geocoded_response.postal_code
#     address["extension"] = []
#     address["extension"].append(
#         {
#             "url": "http://hl7.org/fhir/StructureDefinition/geolocation",
#             "extension": [
#                 {"url": "latitude", "valueDecimal": geocoded_response.lat},
#                 {"url": "longitude", "valueDecimal": geocoded_response.lng},
#             ],
#         }
#     )
#     address["_line"] = []
#     address["_line"].append(
#         {
#             "extension": [
#                 {
#                     "url": "http://hl7.org/fhir/StructureDefinition"
#                     + "/iso21090-ADXP-censusTract",
#                     "valueString": "59",
#                 }
#             ]
#         },
#     )

#     returned_bundle = census_client.geocode_bundle(bundle, overwrite=False)
#     print(f"Returned_bundle address: {returned_bundle['entry'][1]['resource']}")
#     print()
#     print(f"standardized_bundle address: {standardized_bundle['entry'][1]['resource']}")
#     # assert standardized_bundle == returned_bundle


# #     assert bundle != standardized_bundle
