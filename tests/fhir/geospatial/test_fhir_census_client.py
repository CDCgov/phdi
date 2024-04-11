import copy
import json
import pathlib

import pytest

from phdi.fhir.geospatial.census import CensusFhirGeocodeClient
from phdi.geospatial.core import GeocodeResult

FHIR_BUNDLE_PATH = pathlib.Path(__file__).parent.parent.parent / "assets" / "general"


@pytest.fixture
def patient_bundle_census():
    with open(FHIR_BUNDLE_PATH / "patient_bundle_census.json") as file:
        return json.load(file)


@pytest.fixture
def patient_bundle_census_extension():
    with open(FHIR_BUNDLE_PATH / "patient_bundle_census_extension.json") as file:
        return json.load(file)


@pytest.fixture
def geocoded_response():
    return GeocodeResult(
        line=["239 Greene St", "Apt 4L"],
        city="NEW YORK",
        state="NY",
        lat=40.729656537689166,
        lng=-73.99550002689155,
        county_fips="36061",
        county_name="New York",
        postal_code="10003",
        census_tract="59",
    )


@pytest.fixture
def census_client(monkeypatch, geocoded_response):
    client = CensusFhirGeocodeClient()

    def mock_geocode_from_dict(*args, **kwargs):
        return geocoded_response

    monkeypatch.setattr(
        client._CensusFhirGeocodeClient__client,
        "geocode_from_dict",
        mock_geocode_from_dict,
    )

    return client


def _get_patient_from_bundle(bundle):
    return bundle["entry"][1]["resource"]


def _extract_address(standardized_patient, geocoded_response, extension=False):
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
    if extension:
        address["_line"][0]["extension"].append(
            {
                "url": "http://hl7.org/fhir/StructureDefinition/"
                + "iso21090-ADXP-censusTract",
                "valueString": "59",
            }
        )
        address["_line"][1] = {
            "extension": [
                {
                    "url": "http://hl7.org/fhir/StructureDefinition/"
                    + "iso21090-ADXP-censusTract",
                    "valueString": "59",
                }
            ]
        }
    else:
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
    return address


def test_geocode_resource_census(
    patient_bundle_census,
    patient_bundle_census_extension,
    geocoded_response,
    census_client,
):
    assert census_client is not None

    patient = _get_patient_from_bundle(patient_bundle_census)
    standardized_patient = copy.deepcopy(patient)
    _extract_address(standardized_patient, geocoded_response)

    # Case 1: Overwrite = False
    returned_patient = census_client.geocode_resource(patient, overwrite=False)
    assert standardized_patient == returned_patient
    assert returned_patient.get("address") != patient.get("address")
    assert returned_patient.get("address")[0].get("line") == ["239 Greene St", "Apt 4L"]

    # Case 2: Overwrite = True
    returned_patient = census_client.geocode_resource(patient, overwrite=True)
    assert returned_patient["address"][0].get("line") == [
        "239 Greene St",
        "Apt 4L",
    ]
    assert returned_patient == patient

    # Case 3: Patient already has an extension on line, and it's preserved.
    patient = _get_patient_from_bundle(patient_bundle_census_extension)
    standardized_patient = copy.deepcopy(patient)
    _extract_address(standardized_patient, geocoded_response, extension=True)

    # Case 3: Patient already has 1 extension on _line, and it's preserved.
    returned_patient = census_client.geocode_resource(patient, overwrite=True)

    assert returned_patient == standardized_patient
    assert returned_patient.get("address")[0].get("_line")[0].get("extension")[0] == {
        "existing_url": "existing_extension"
    }
    assert (
        returned_patient.get("address")[0].get("_line")[1].get("extension")[0]
        is not None
    )


def test_geocode_bundle_census(patient_bundle_census, geocoded_response, census_client):
    assert census_client is not None

    standardized_bundle = copy.deepcopy(patient_bundle_census)
    patient = _get_patient_from_bundle(standardized_bundle)
    _extract_address(patient, geocoded_response)

    returned_bundle = census_client.geocode_bundle(
        patient_bundle_census, overwrite=False
    )
    assert standardized_bundle == returned_bundle
    assert patient_bundle_census != standardized_bundle
