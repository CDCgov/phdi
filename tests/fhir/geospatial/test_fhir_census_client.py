from unittest import mock
import json
import pathlib
import copy

from phdi.fhir.geospatial.census import CensusFhirGeocodeClient
from phdi.geospatial.core import GeocodeResult


def test_geocode_resource_census():
    census_client = CensusFhirGeocodeClient()
    assert census_client is not None

    geocoded_response = GeocodeResult(
        line=["239 GREENE ST", "APT 4L"],
        city="NEW YORK",
        state="NY",
        lat=45.123,
        lng=-70.234,
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
    address["line"] = geocoded_response.line
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
                    "url": "http://hl7.org/fhir/StructureDefinition/iso21090-ADXP-censusTract",
                    "valueString": "59",
                }
            ]
        },
        {
            "extension": [
                {
                    "url": "http://hl7.org/fhir/StructureDefinition/iso21090-ADXP-censusTract",
                    "valueString": "59",
                }
            ]
        },
    )

    # census_client.geocode_from_str = mock.Mock()
    # census_client.geocode_from_str.return_value = geocoded_response

    # Case 1: Overwrite = False
    returned_patient = census_client.geocode_resource(patient, overwrite=False)
    print(f"Returned Patient:{returned_patient['address']}")
    # print(f"Standardized Patient:{standardized_patient['address']}")
    print(f"Patient:{patient['address']}")
    # assert standardized_patient == returned_patient
    assert returned_patient != patient

    # # Case 2: Overwrite = True
    # assert standardized_patient == census_client.geocode_resource(patient)
    # census_client.geocode_from_str.assert_called()


def test_geocode_bundle():
    census_client = CensusFhirGeocodeClient()
    assert census_client is not None


#     geocoded_response = GeocodeResult(
#         line=["123 FAKE ST"],
#         city="New York",
#         state="NY",
#         lat=45.123,
#         lng=-70.234,
#         county_fips="36061",
#         county_name="New York",
#         postal_code="10001",
#         precision="Zip9",
#     )

#     bundle = json.load(
#         open(
#             pathlib.Path(__file__).parent.parent.parent
#             / "assets"
#             / "patient_bundle.json"
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

#     census_client.geocode_from_str = mock.Mock()
#     census_client.geocode_from_str.return_value = geocoded_response
#     returned_bundle = census_client.geocode_bundle(bundle, overwrite=False)
#     assert standardized_bundle == returned_bundle
#     assert bundle != standardized_bundle
#     census_client.geocode_from_str.assert_called()
