import pathlib
from fastapi.testclient import TestClient
from unittest import mock
from app.main import (
    app,
    message_validators,
    validate_ecr_msg,
    validate_elr_msg,
    validate_vxu_msg,
    validate_fhir_bundle,
)

client = TestClient(app)
test_error_types = ["errors", "warnings", "information"]


# Test bad file
sample_file_bad = open(
    pathlib.Path(__file__).parent.parent.parent.parent
    / "tests"
    / "assets"
    / "validation"
    / "ecr_sample_input_bad.xml"
).read()

# Test good file with RR data
sample_file_good_with_RR = open(
    pathlib.Path(__file__).parent.parent.parent.parent
    / "tests"
    / "assets"
    / "validation"
    / "ecr_sample_input_good_with_RR.xml"
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
                "Could not find field. Field name: 'Status' "
                + "Attributes: attribute #1: 'code' with the "
                + "required value pattern: 'RRVS19|RRVS20|RRVS21|"
                + "RRVS22', attribute #2: 'codeSystem', attribute #3: "
                + "'displayName'",
                "Could not find field. Field name: "
                + "'Conditions' Attributes: attribute #1: 'code' "
                + "with the required value pattern: '[0-9]+',"
                + " attribute #2: 'codeSystem'",
                "The field value does not exist or doesn't match "
                + "the following pattern: "
                + "'[0-9]{5}(?:-[0-9]{4})?'. For the Field name: 'Zip' value: '9999'",
            ],
            "errors": [
                "Could not find field. Field name: 'First Name' Related elements: "
                + "Field name: 'name' Attributes: attribute #1: 'use' with the "
                + "required value pattern: 'L'"
            ],
            "warnings": [
                "Could not find field. Field name: 'eICR Version Number' "
                + "Attributes: attribute #1: 'value'",
                "Attribute: 'code' "
                + "not in expected format. Field name: 'Sex' Attributes: "
                + "attribute #1: 'code' with the required value pattern: "
                + "'F|M|O|U' actual value: 't', attribute #2: 'codeSystem'"
                + " actual value: '2.16.840.1.113883.5.1'",
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


@mock.patch("app.main.message_validators")
def test_validate_endpoint_valid_vxu(patched_message_validators):
    for message_type in message_validators:
        # Prepare mocked validator function
        validation_response = {"message_valid": True, "validation_results": {}}
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
