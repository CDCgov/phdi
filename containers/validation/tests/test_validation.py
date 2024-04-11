import pathlib

from app.main import app
from app.main import validate_ecr_msg
from app.main import validate_elr_msg
from app.main import validate_fhir_bundle
from app.main import validate_vxu_msg
from fastapi.testclient import TestClient

client = TestClient(app)
test_error_types = ["errors", "warnings", "information"]


# Test bad file
sample_file_bad = open(
    pathlib.Path(__file__).parent / "assets" / "ecr_sample_input_bad.xml"
).read()

# Test good file with RR data
sample_file_good_with_RR = open(
    pathlib.Path(__file__).parent / "assets" / "ecr_sample_input_good_with_RR.xml"
).read()


def test_validate_ecr_invalid_xml():
    expected_result2 = {
        "message_valid": False,
        "validation_results": {
            "fatal": ["eCR Message is not valid XML!"],
            "errors": [],
            "warnings": [],
            "information": [],
            "message_ids": {},
        },
    }
    actual_result2 = validate_ecr_msg(
        message="my ecr contents", include_error_types=test_error_types
    )
    assert actual_result2 == expected_result2


def test_validate_ecr_valid():
    actual_result1 = validate_ecr_msg(
        message=sample_file_good_with_RR, include_error_types=test_error_types
    )
    expected_result1 = {
        "message_valid": True,
        "validation_results": {
            "fatal": [],
            "errors": [],
            "warnings": [],
            "information": ["Validation completed with no fatal errors!"],
            "message_ids": {
                "eicr": {
                    "root": "2.16.840.1.113883.9.9.9.9.9",
                    "extension": "db734647-fc99-424c-a864-7e3cda82e704",
                },
                "rr": {
                    "root": "4efa0e5c-c34c-429f-b5de-f1a13aef4a28",
                    "extension": None,
                },
            },
        },
    }
    assert actual_result1 == expected_result1


def test_validate_ecr_invalid():
    expected_result3 = {
        "message_valid": False,
        "validation_results": {
            "fatal": [
                "Could not find field. Field name: "
                "'eICR Version Number' "
                "Attributes: attribute #1: 'value'",
                "Could not find field. Field name: "
                "'City' Related elements: Field name:"
                " 'addr' Attributes: attribute #1: 'use'"
                " with the required value pattern: 'H'",
                "The field value does not exist or doesn't"
                " match the following pattern: "
                "'[0-9]{5}(?:-[0-9]{4})?'. "
                "For the Field name: 'Zip' value: '9999'",
            ],
            "errors": ["Could not find field. Field name: 'First Name'"],
            "warnings": [
                "Attribute: 'code' not in expected format."
                " Field name: 'Sex' Attributes: "
                "attribute #1: 'code' with the required value "
                "pattern: 'F|M|O|U' actual value: 't', "
                "attribute #2: 'codeSystem' actual value: '2.16.840.1.113883.5.1'"
            ],
            "information": [],
            "message_ids": {
                "eicr": {
                    "root": "2.16.840.1.113883.9.9.9.9.9",
                    "extension": "db734647-fc99-424c-a864-7e3cda82e704",
                },
                "rr": {},
            },
        },
    }
    actual_result3 = validate_ecr_msg(
        message=sample_file_bad, include_error_types=test_error_types
    )
    assert actual_result3 == expected_result3


def test_validate_elr():
    result = validate_elr_msg("my elr contents", test_error_types)
    assert result == {
        "message_valid": True,
        "validation_results": {
            "details": "No validation was actually performed. Validation for ELR is "
            "only stubbed currently."
        },
    }


def test_validate_vxu():
    result = validate_vxu_msg("my vxu contents", test_error_types)
    assert result == {
        "message_valid": True,
        "validation_results": {
            "details": "No validation was actually performed. Validation for VXU is "
            "only stubbed currently."
        },
    }


def test_validate_fhir_bundle():
    result = validate_fhir_bundle("my fhir bundle contents", test_error_types)
    assert result == {
        "message_valid": True,
        "validation_results": {
            "details": "No validation was actually performed. Validation for FHIR is "
            "only stubbed currently."
        },
    }
