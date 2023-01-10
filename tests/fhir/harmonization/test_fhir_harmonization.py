import fuzzy
import json
import pathlib
import copy

from phdi.fhir.harmonization import (
    double_metaphone_bundle,
    double_metaphone_patient,
    standardize_names,
    standardize_phones,
)


def test_double_metaphone_bundle():
    raw_bundle = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "FHIR_server_extracted_data.json"
        )
    )
    raw_bundle = standardize_names(raw_bundle)
    dms = double_metaphone_bundle(raw_bundle)
    assert dms == {
        "907844f6-7c99-eabc-f68e-d92189729a55": [
            {"official": [[b"KMPR", None], [b"PRK", None]]}
        ],
        "65489-asdf5-6d8w2-zz5g8": [
            {"official": [[b"JN", b"AN"], [b"TPRS", None], [b"XPRT", None]]}
        ],
        "some-uuid": [{"official": [[b"JN", b"AN"], [b"TNJR", b"TNKR"], [None, None]]}],
    }


def test_double_metaphone_patient():
    raw_bundle = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "patient_bundle.json"
        )
    )

    # Add a couple more name uses to prove out robustness
    patient = raw_bundle.get("entry")[1].get("resource")
    patient.get("name").append({"family": "D", "given": ["Johnny"], "use": "usual"})
    patient.get("name").append(
        {"family": "Doe", "given": ["Johnathan", "Dangerson"], "use": "old"}
    )

    # Standardize all of the names
    patient = standardize_names(patient)

    # Now test and verify using preexisting and new dmeta objects
    for dmeta in [None, fuzzy.DMetaphone()]:
        dms = double_metaphone_patient(patient, dmeta)
        assert dms == [
            {"official": [[b"JN", b"AN"], [b"TNJR", b"TNKR"], [b"T", None]]},
            {"usual": [[b"JN", b"AN"], [b"T", None]]},
            {"old": [[b"JN0N", b"ANTN"], [b"TNJR", b"TNKR"], [b"T", None]]},
        ]


def test_standardize_names():
    raw_bundle = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
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
