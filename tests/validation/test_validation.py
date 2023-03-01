import pathlib

import yaml
from phdi.validation.validation import validate_ecr


# Test file with known errors
sample_file_bad = open(
    pathlib.Path(__file__).parent.parent / "assets" / "ecr_sample_input_bad.xml"
).read()


# Test good file
sample_file_good = open(
    pathlib.Path(__file__).parent.parent / "assets" / "ecr_sample_input_good.xml"
).read()

with open(
    pathlib.Path(__file__).parent.parent / "assets" / "sample_ecr_config.yaml", "r"
) as file:
    config = yaml.safe_load(file)


def test_validate_good():
    expected_response = {
        "message_valid": True,
        "validation_results": {
            "errors": [],
            "warnings": [],
            "information": ["Validation complete with no errors!"],
        },
    }
    result = validate_ecr(
        ecr_message=sample_file_good,
        config=config,
        error_types=["error", "warn", "info"],
    )

    assert result == expected_response


def test_validate_bad():
    expected_response = {
        "message_valid": False,
        "validation_results": {
            "errors": [
                "Could not find field: {'fieldName': 'eICR Version Number', "
                + "'cdaPath': '//hl7:ClinicalDocument/hl7:versionNumber', "
                + "'attributes': [{'attributeName': 'value'}]}",
                "Could not find field: {'fieldName': 'First "
                + "Name', 'cdaPath': "
                + "'//hl7:ClinicalDocument/hl7:recordTarget/hl7:patientRole/"
                + "hl7:patient/hl7:name/hl7:given', "
                + "'textRequired': 'True', 'parent': 'name', "
                + "'parent_attributes': [{'attributeName': "
                + "'use', 'regEx': 'L'}]}",
                "Attribute: 'use' for field: 'Address' not in expected format",
                "Could not find field: {'fieldName': "
                + "'City', 'cdaPath': "
                + "'//hl7:ClinicalDocument/hl7:recordTarget/hl7:patientRole/hl7:addr/"
                + "hl7:city', "
                + "'textRequired': 'True', 'parent': 'addr', "
                + "'parent_attributes': [{'attributeName': "
                + "'use', 'regEx': 'H'}]}",
                "Field: Zip does not match regEx: [0-9]{5}(?:-[0-9]{4})?",
            ],
            "warnings": [],
            "information": [],
        },
    }
    result = validate_ecr(
        ecr_message=sample_file_bad,
        config=config,
        error_types=["error", "warn", "info"],
    )

    assert result == expected_response
