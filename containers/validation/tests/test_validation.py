import pathlib
from fastapi.testclient import TestClient
from unittest import mock
from app.main import (
    app,
    message_validators,
    validate_ecr_msg,
    validate_elr_msg,
    validate_vxu_msg,
)

client = TestClient(app)
test_error_types = ["errors", "warnings", "information"]
# Test good file
sample_file_good = open(
    pathlib.Path(__file__).parent.parent.parent.parent
    / "tests"
    / "assets"
    / "ecr_sample_input_good.xml"
).read()
# Test bad file
sample_file_bad = open(
    pathlib.Path(__file__).parent.parent.parent.parent
    / "tests"
    / "assets"
    / "ecr_sample_input_bad.xml"
).read()


def test_health_check():
    actual_response = client.get("/")
    assert actual_response.status_code == 200
    assert actual_response.json() == {"status": "OK"}


def test_validate_ecr_invalid_xml():
    expected_result2 = {
        "message_valid": False,
        "validation_results": {
            "fatal": ["eCR Message is not valid XML!"],
            "errors": [],
            "warnings": [],
            "information": [],
        },
        "validated_message": None,
    }
    actual_result2 = validate_ecr_msg(
        message="my ecr contents", include_error_types=test_error_types
    )
    assert actual_result2 == expected_result2


def test_validate_ecr_valid():
    actual_result1 = validate_ecr_msg(
        message=sample_file_good, include_error_types=test_error_types
    )
    expected_result1 = {
        "message_valid": True,
        "validation_results": {
            "fatal": [],
            "errors": [],
            "warnings": [],
            "information": ["Validation completed with no fatal errors!"],
        },
        "validated_message": sample_file_good,
    }
    assert actual_result1 == expected_result1


def test_validate_ecr_invalid():
    # TODO: we need to clean up the error messages
    # we don't need to see all the xpath data within the error
    # just the field, value, and why it failed
    expected_result3 = {
        "message_valid": False,
        "validation_results": {
            "errors": [],
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
            "warnings": ["Attribute: 'code' for field: 'Sex' not in expected format"],
            "information": [],
        },
        "validated_message": None,
    }
    actual_result3 = validate_ecr_msg(
        message=sample_file_bad, include_error_types=test_error_types
    )
    print(actual_result3)
    assert actual_result3 == expected_result3


def test_validate_elr():
    assert validate_elr_msg("my elr contents", test_error_types) == {
        "message_valid": True,
        "validation_results": {
            "details": "No validation was actually preformed. This endpoint only has "
            "stubbed functionality"
        },
        "validated_message": None,
    }


def test_validate_vxu():
    assert validate_vxu_msg("my vxu contents", test_error_types) == {
        "message_valid": True,
        "validation_results": {
            "details": "No validation was actually preformed. This endpoint only has "
            "stubbed functionality"
        },
        "validated_message": None,
    }


@mock.patch("app.main.message_validators")
def test_validate_endpoint_valid_vxu(patched_message_validators):
    for message_type in message_validators:
        # Prepare mocked validator function
        validation_response = {
            "message_valid": True,
            "validation_results": {},
            "validated_message": {},
        }
        mocked_validator = mock.Mock()
        mocked_validator.return_value = validation_response
        message_validators_dict = {message_type: mocked_validator}
        patched_message_validators.__getitem__.side_effect = (
            message_validators_dict.__getitem__
        )

        # Send request to test client
        request_body = {
            "message_type": message_type,
            "include_error_types": "",
            "message": "message contents",
        }
        actual_response = client.post("/validate", json=request_body)

        # Check that the correct validator was selected and used properly.
        assert actual_response.status_code == 200
        message_validators_dict[message_type].assert_called_with(
            message=request_body["message"], include_error_types=[]
        )
