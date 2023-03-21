import pathlib
from phdi.validation.validation import (
    _organize_error_messages,
    _response_builder,
    _append_error_message,
    _add_message_ids,
    _clear_all_errors_and_ids,
    ERROR_MESSAGES
)


test_include_errors = ["fatal", "errors", "warnings", "information"]

# Test file with known errors
sample_file_bad = open(
    pathlib.Path(__file__).parent.parent / "assets" / "ecr_sample_input_bad.xml"
).read()


# Test good file
sample_file_good = open(
    pathlib.Path(__file__).parent.parent / "assets" / "ecr_sample_input_good.xml"
).read()

# Test good file with RR data
sample_file_good_RR = open(
    pathlib.Path(__file__).parent.parent
    / "assets"
    / "ecr_sample_input_good_with_RR.xml"
).read()

config = open(
    pathlib.Path(__file__).parent.parent / "assets" / "sample_ecr_config.yaml"
).read()


def test_organize_error_messages():
    fatal = ["foo"]
    errors = ["my error1", "my_error2"]
    warns = ["my warn1"]
    infos = ["", "SOME"]
    test_include_errors = ["fatal", "errors", "warnings", "information"]
    msg_ids = []

    expected_result = {
        "fatal": fatal,
        "errors": errors,
        "warnings": warns,
        "information": ["SOME"],
        "message_ids": msg_ids,
    }

    _append_error_message("fatal",fatal)
    _append_error_message("warnings", warns)
    _append_error_message("errors", errors)
    _append_error_message("information", infos)
    _add_message_ids(msg_ids)

    _organize_error_messages(include_error_types=test_include_errors)
    assert ERROR_MESSAGES == expected_result

    fatal = []
    test_include_errors = ["information"]

    expected_result = {
        "fatal": [],
        "errors": [],
        "warnings": [],
        "information": ["SOME"],
        "message_ids": msg_ids,
    }
    _clear_all_errors_and_ids()
    _append_error_message("fatal", [])
    _append_error_message("warnings", [])
    _append_error_message("information", infos)
    _add_message_ids(msg_ids)

    _organize_error_messages(include_error_types=test_include_errors)

    print("HERE:")
    print(ERROR_MESSAGES)
    print(expected_result)
    
    assert ERROR_MESSAGES == expected_result


def test_response_builder():
    expected_response = {
        "message_valid": True,
        "validation_results": {
            "fatal": [],
            "errors": [],
            "warnings": [],
            "information": ["Validation completed with no fatal errors!"],
            "message_ids": {},
        },
        "validated_message": sample_file_good,
    }
    result = _response_builder(
        errors=expected_response["validation_results"],
        msg=sample_file_good,
        include_error_types=test_include_errors,
    )

    assert result == expected_response
