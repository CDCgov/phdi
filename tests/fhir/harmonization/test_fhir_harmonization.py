import copy
import json
import pathlib

from phdi.fhir.harmonization import double_metaphone_bundle
from phdi.fhir.harmonization import double_metaphone_patient
from phdi.fhir.harmonization import standardize_dob
from phdi.fhir.harmonization import standardize_names
from phdi.fhir.harmonization import standardize_phones
from phdi.harmonization import DoubleMetaphone


def test_double_metaphone_bundle():
    raw_bundle = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "general"
            / "FHIR_server_extracted_data.json"
        )
    )
    raw_bundle = standardize_names(raw_bundle)
    dm_bundle = double_metaphone_bundle(raw_bundle, overwrite=False)
    dms = {
        "907844f6-7c99-eabc-f68e-d92189729a55": {
            "familyName": ["PRS", ""],  # Price
            "givenName": [["KMPR", ""]],  # Kimberly
        },
        "65489-asdf5-6d8w2-zz5g8": {
            "givenName": [["JN", "AN"], ["TPRS", ""]],  # John Tiberius
            "familyName": ["XPRT", ""],  # Shepard
        },
        "some-uuid": {
            "givenName": [["JN", "AN"], ["TNJR", "TNKR"]],  # John Danger
            "familyName": ["", ""],  # No family name
        },
    }

    for entry in dm_bundle.get("entry"):
        resource = entry.get("resource")
        if resource.get("resourceType") == "Patient":
            for name in resource.get("name"):
                for extension in name.get("extension"):
                    if "metaphone" in extension.get("url").lower():
                        for dm_name in extension.get("extension"):
                            type = dm_name.get("url")
                            assert dms[resource.get("id")][type] == dm_name.get(
                                "valueString"
                            )


def test_double_metaphone_patient():
    raw_bundle = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "general"
            / "patient_bundle.json"
        )
    )

    # Add a couple more name uses to prove out robustness, and create
    # a second patient with a variety of "non-English" sounding names
    patient_1 = raw_bundle.get("entry")[1].get("resource")
    patient_1.get("name").append({"family": "D", "given": ["Johnny"], "use": "usual"})
    patient_1.get("name").append(
        {"family": "Doe", "given": ["Johnathan", "Dangerson"], "use": "old"}
    )
    patient_2 = {
        "id": "test-patient-2",
        "name": [
            {
                "use": "official",
                "family": "Hernandez",
                "given": ["Dominic", "Alejandro", "Diego"],
            },
            {"use": "nickname", "family": "Hernandez", "given": ["Dom"]},
            {
                "use": "temp",
                "family": "Rodriguez",
                "given": ["Xavier", "Jorge", "Eduardo"],
            },
        ],
    }

    # DM Answers
    dms_1 = {
        "official": {
            "givenName": [["JN", "AN"], ["TNJR", "TNKR"]],
            "familyName": ["T", ""],
        },
        "usual": {"givenName": [["JN", "AN"]], "familyName": ["T", ""]},
        "old": {
            "givenName": [["JN0N", "ANTN"], ["TNJR", "TNKR"]],
            "familyName": ["T", ""],
        },
    }
    dms_2 = {
        "official": {
            "givenName": [["TMNK", ""], ["ALJN", "ALHN"], ["TK", ""]],
            "familyName": ["HRNN", ""],
        },
        "nickname": {"givenName": [["TM", ""]], "familyName": ["HRNN", ""]},
        "temp": {
            "givenName": [["SF", "SFR"], ["JRJ", "ARK"], ["ATRT", ""]],
            "familyName": ["RTRK", ""],
        },
    }

    patients = [patient_1, patient_2]
    dms = [dms_1, dms_2]
    for i in range(len(patients)):
        dm_answers = dms[i]

        # Standardize all of the names
        patient = standardize_names(patients[i])

        # Now test and verify using preexisting and new dmeta objects
        for dmeta in [None, DoubleMetaphone()]:
            dm_patient = double_metaphone_patient(patient, dmeta, overwrite=False)

            for name in dm_patient.get("name", []):
                for extension in name.get("extension"):
                    if "metaphone" in extension.get("url").lower():
                        assert (
                            extension.get("url")
                            == "https://xlinux.nist.gov/dads/HTML/doubleMetaphone.html"
                        )
                        assert len(extension.get("extension")) == 2
                        for dm_name in extension.get("extension"):
                            type = dm_name.get("url")
                            assert dm_answers[name.get("use")][type] == dm_name.get(
                                "valueString"
                            )


def test_standardize_names():
    raw_bundle = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "general"
            / "patient_bundle.json"
        )
    )

    # Case where we pass in a whole FHIR bundle
    standardized_bundle = copy.deepcopy(raw_bundle)
    patient = standardized_bundle["entry"][1]["resource"]
    patient["name"][0]["family"] = "DOE"
    patient["name"][0]["given"] = ["JOHN", "DANGER"]
    assert standardize_names(raw_bundle) == standardized_bundle

    # Case when we don't want to overwrite the data for a bundle
    standardized_bundle = copy.deepcopy(raw_bundle)
    patient = standardized_bundle["entry"][1]["resource"]
    patient["name"][0]["family"] = "DOE"
    patient["name"][0]["given"] = ["JOHN", "DANGER"]
    assert standardize_names(raw_bundle, overwrite=True) == standardized_bundle

    # Case where we provide only a single resource
    patient_resource = raw_bundle["entry"][1]["resource"]
    standardized_patient = copy.deepcopy(patient_resource)
    standardized_patient["name"][0]["family"] = "DOE"
    standardized_patient["name"][0]["given"] = ["JOHN", "DANGER"]
    assert standardize_names(patient_resource) == standardized_patient

    # Case when we don't want to overwrite the data for a single resource
    patient_resource = raw_bundle["entry"][1]["resource"]
    standardized_patient = copy.deepcopy(patient_resource)
    standardized_patient["name"][0]["family"] = "DOE"
    standardized_patient["name"][0]["given"] = ["JOHN", "DANGER"]
    assert standardize_names(patient_resource, overwrite=False) == standardized_patient


def test_standardize_phones():
    raw_bundle = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "general"
            / "patient_bundle.json"
        )
    )

    # Case where we pass in a whole FHIR bundle
    standardized_bundle = copy.deepcopy(raw_bundle.copy())
    patient = standardized_bundle["entry"][1]["resource"]
    patient["telecom"][0]["value"] = "+11234567890"
    assert standardize_phones(raw_bundle) == standardized_bundle

    # Case where we pass in a whole FHIR bundle and do not overwrite the data
    standardized_bundle = copy.deepcopy(raw_bundle.copy())
    patient = standardized_bundle["entry"][1]["resource"]
    patient["telecom"][0]["value"] = "+11234567890"
    assert standardize_phones(raw_bundle, overwrite=False) == standardized_bundle

    # Case where we provide only a single resource
    patient_resource = raw_bundle["entry"][1]["resource"]
    standardized_patient = copy.deepcopy(patient_resource)
    standardized_patient["telecom"][0]["value"] = "+11234567890"
    assert standardize_phones(patient_resource) == standardized_patient

    # Case where we provide only a single resource and do not overwrite the data
    patient_resource = raw_bundle["entry"][1]["resource"]
    standardized_patient = copy.deepcopy(patient_resource)
    standardized_patient["telecom"][0]["value"] = "+11234567890"
    assert standardize_phones(patient_resource, overwrite=False) == standardized_patient

    # Case where the input data has no country information in the address
    patient_resource = raw_bundle["entry"][1]["resource"]
    patient_resource.get("address")[0].pop("country")
    assert patient_resource.get("address")[0].get("country") is None
    standardized_patient = copy.deepcopy(patient_resource)
    standardized_patient["telecom"][0]["value"] = "+11234567890"
    assert standardize_phones(patient_resource) == standardized_patient

    # Case where the input data has no country information in the address and we do not
    # overwrite the data
    patient_resource = raw_bundle["entry"][1]["resource"]
    assert patient_resource.get("address")[0].get("country") is None
    standardized_patient = copy.deepcopy(patient_resource)
    standardized_patient["telecom"][0]["value"] = "+11234567890"
    assert standardize_phones(patient_resource, overwrite=False) == standardized_patient


def test_standardize_dob():
    raw_bundle = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "general"
            / "patient_bundle.json"
        )
    )

    # Case where we pass in a whole FHIR bundle
    standardized_bundle = copy.deepcopy(raw_bundle.copy())
    raw_bundle_updated = copy.deepcopy(raw_bundle.copy())
    patient = standardized_bundle["entry"][1]["resource"]
    patient["birthDate"] = "02/1983/01"
    raw_bundle_updated["entry"][1]["resource"] = patient
    assert standardize_dob(raw_bundle_updated, "%m/%Y/%d") == standardized_bundle

    # Case where we pass in a whole FHIR bundle and do not overwrite the data
    standardized_bundle = copy.deepcopy(raw_bundle.copy())
    raw_bundle_updated = copy.deepcopy(raw_bundle.copy())
    patient = standardized_bundle["entry"][1]["resource"]
    patient["birthDate"] = "02/1983/01"
    raw_bundle_updated["entry"][1]["resource"] = patient
    assert (
        standardize_dob(raw_bundle_updated, "%m/%Y/%d", overwrite=False)
        == standardized_bundle
    )

    # Case where we provide only a single resource
    standardized_bundle = copy.deepcopy(raw_bundle.copy())
    patient = standardized_bundle["entry"][1]["resource"]
    standardized_patient = copy.deepcopy(patient)
    patient_updated = copy.deepcopy(patient)
    patient_updated["birthDate"] = "02/1983/01"
    assert standardize_dob(patient_updated, "%m/%Y/%d") == standardized_patient

    # Case where we provide only a single resource and do not overwrite the data
    standardized_bundle = copy.deepcopy(raw_bundle.copy())
    patient = standardized_bundle["entry"][1]["resource"]
    standardized_patient = copy.deepcopy(patient)
    patient_updated = copy.deepcopy(patient)
    patient_updated["birthDate"] = "02/1983/01"
    assert (
        standardize_dob(patient_updated, "%m/%Y/%d", overwrite=False) == patient_updated
    )
