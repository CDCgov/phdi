import pathlib

import yaml
from phdi.validation.validation import validate_ecr


test_include_errors = ["fatal", "errors", "warnings", "information"]

# Test file with known errors
sample_file_bad = open(
    pathlib.Path(__file__).parent.parent / "assets" / "ecr_sample_input_bad.xml"
).read()


# Test good file
sample_file_good = open(
    pathlib.Path(__file__).parent.parent / "assets" / "ecr_sample_input_good.xml"
).read()

# Test file with error
sample_file_error = open(
    pathlib.Path(__file__).parent.parent / "assets" / "ecr_sample_input_error.xml"
).read()

with open(
    pathlib.Path(__file__).parent.parent / "assets" / "sample_ecr_config.yaml", "r"
) as file:
    config = yaml.safe_load(file)


def test_validate_good():
    expected_response = {
        "message_valid": True,
        "validation_results": {
            "fatal": [],
            "errors": [],
            "warnings": [],
            "information": ["Validation completed with no fatal errors!"],
        },
        "validated_message": sample_file_good,
    }
    result = validate_ecr(
        ecr_message=sample_file_good,
        config=config,
        include_error_types=test_include_errors,
    )
    assert result == expected_response


def test_validate_bad():
    # TODO: we need to clean up the error messages
    # we don't need to see all the xpath data within the error
    # just the field, value, and why it failed
    expected_response = {
        "message_valid": False,
        "validation_results": {
            "fatal": [
                "Could not find field: {'fieldName': 'eICR Version Number', "
                + "'cdaPath': '//hl7:ClinicalDocument/hl7:versionNumber', "
                + "'errorType': 'fatal', "
                + "'attributes': [{'attributeName': 'value'}]}",
                "Could not find field: {'fieldName': 'First "
                + "Name', 'cdaPath': "
                + "'//hl7:ClinicalDocument/hl7:recordTarget/hl7:patientRole/"
                + "hl7:patient/hl7:name/hl7:given', "
                + "'errorType': 'fatal', "
                + "'textRequired': 'True', 'parent': 'name', "
                + "'parent_attributes': [{'attributeName': "
                + "'use', 'regEx': 'L'}]}",
                "Could not find field: {'fieldName': "
                + "'City', 'cdaPath': "
                + "'//hl7:ClinicalDocument/hl7:recordTarget/hl7:patientRole/hl7:addr/"
                + "hl7:city', "
                + "'errorType': 'fatal', "
                + "'textRequired': 'True', 'parent': 'addr', "
                + "'parent_attributes': [{'attributeName': "
                + "'use', 'regEx': 'H'}]}",
                "Field: Zip does not match regEx: [0-9]{5}(?:-[0-9]{4})?",
            ],
            "errors": [],
            "warnings": ["Attribute: 'code' for field: 'Sex' not in expected format"],
            "information": [],
        },
        "validated_message": None,
    }
    result = validate_ecr(
        ecr_message=sample_file_bad,
        config=config,
        include_error_types=test_include_errors,
    )
    assert result == expected_response


def test_validate_error():
    expected_response = {
        "message_valid": True,
        "validation_results": {
            "fatal": [],
            "errors": [
                "Could not find field: {'fieldName': 'Status', 'cdaPath': "
                + "'//hl7:ClinicalDocument/hl7:component/hl7:structuredBody"
                + "/hl7:component/hl7:section/hl7:entry/hl7:act/hl7:code', "
                + "'errorType': 'errors', 'attributes': [{'attributeName': "
                + "'code'}]}"
            ],
            "warnings": [],
            "information": ["Validation completed with no fatal errors!"],
        },
        "validated_message": sample_file_error,
    }
    result = validate_ecr(
        ecr_message=sample_file_error,
        config=config,
        include_error_types=["fatal", "errors", "warnings", "information"],
    )
    assert result == expected_response


def test_validate_ecr_invalid_xml():
    expected_response = {
        "message_valid": False,
        "validation_results": {
            "fatal": ["eCR Message is not valid XML!"],
            "errors": [],
            "warnings": [],
            "information": [],
        },
        "validated_message": None,
    }
    result = validate_ecr(
        ecr_message=" BLAH ",
        config=config,
        include_error_types=test_include_errors,
    )
    assert result == expected_response
