import json
import pathlib

from phdi.fhir.utils import (
    find_resource_by_type,
    get_field,
    _get_fhir_conversion_settings,
)

# @TODO: Write a test case for convert to fhir once the CredsManager and
# request_with_reauth are back in the codebase


def test_get_fhir_conversion_settings():

    # HL7 case (using the demo message from the HL7 API walkthrough)
    message = ""
    with open(pathlib.Path(__file__).parent.parent / "assets" / "sample_hl7.hl7") as fp:
        message = fp.read()
    settings = _get_fhir_conversion_settings(message)
    assert settings == {
        "root_template": "ORU_R01",
        "input_data_type": "HL7v2",
        "template_collection": "microsofthealth/fhirconverter:default",
    }

    # CCDA case (using an example message found at https://github.com/HL7/C-CDA-Examples)
    message = ""
    with open(
        pathlib.Path(__file__).parent.parent / "assets" / "ccda_sample.xml"
    ) as fp:
        message = fp.read()
    settings = _get_fhir_conversion_settings(message)
    assert settings == {
        "root_template": "ProcedureNote",
        "input_data_type": "Ccda",
        "template_collection": "microsofthealth/ccdatemplates:default",
    }


def test_find_resource_by_type():
    bundle = json.load(
        open(pathlib.Path(__file__).parent.parent / "assets" / "patient_bundle.json")
    )
    found_patients = find_resource_by_type(bundle, "Patient")
    assert len(found_patients) == 1
    assert found_patients[0].get("resource").get("resourceType") == "Patient"


def test_get_field():
    bundle = json.load(
        open(pathlib.Path(__file__).parent.parent / "assets" / "patient_bundle.json")
    )
    patient = bundle["entry"][1]["resource"]
    assert get_field(patient, "telecom", "home", 0) == {
        "use": "home",
        "system": "phone",
        "value": "123-456-7890",
    }
    assert get_field(patient, "telecom", "mobile", 1) == {
        "value": "johndanger@doe.net",
        "system": "email",
    }
