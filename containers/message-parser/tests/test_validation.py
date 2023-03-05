from fastapi.testclient import TestClient
from unittest import mock
from app.main import (
    app,
    message_validators,
    # validate_ecr_msg,
    validate_elr_msg,
    validate_vxu_msg,
)

client = TestClient(app)


def test_health_check():
    actual_response = client.get("/")
    assert actual_response.status_code == 200
    assert actual_response.json() == {"status": "OK"}


# def test_validate_ecr():
#     assert validate_ecr_msg("my ecr contents") == {
#         "message_valid": True,
#         "validation_results": {
#             "details": "No validation was actually preformed. This endpoint only has "
#             "stubbed functionality"
#         },
#     }


def test_validate_elr():
    assert validate_elr_msg("my elr contents", "error") == {
        "message_valid": True,
        "validation_results": {
            "details": "No validation was actually preformed. This endpoint only has "
            "stubbed functionality"
        },
    }


def test_validate_vxu():
    assert validate_vxu_msg("my vxu contents", "error") == {
        "message_valid": True,
        "validation_results": {
            "details": "No validation was actually preformed. This endpoint only has "
            "stubbed functionality"
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
            "include_error_types": "error",
            "message": "message contents",
        }
        actual_response = client.post("/validate", json=request_body)

        # Check that the correct validator was selected and used properly.
        assert actual_response.status_code == 200
        message_validators_dict[message_type].assert_called_with(
            message=request_body["message"], error_types="error"
        )
