import pathlib

from phdi.validation.validation import _add_message_ids
from phdi.validation.validation import _append_error_message
from phdi.validation.validation import _clear_all_errors_and_ids
from phdi.validation.validation import _organize_error_messages
from phdi.validation.validation import _response_builder
from phdi.validation.validation import ERROR_MESSAGES
from tests.test_data_generator import generate_ecr_msg_ids

test_include_errors = ["fatal", "errors", "warnings", "information"]

# Test file with known errors
sample_file_bad = open(
    pathlib.Path(__file__).parent.parent
    / "assets"
    / "validation"
    / "ecr_sample_input_bad.xml"
).read()


# Test good file
sample_file_good = open(
    pathlib.Path(__file__).parent.parent
    / "assets"
    / "validation"
    / "ecr_sample_input_good.xml"
).read()

# Test good file with RR data
sample_file_good_RR = open(
    pathlib.Path(__file__).parent.parent
    / "assets"
    / "validation"
    / "ecr_sample_input_good_with_RR.xml"
).read()

config = open(
    pathlib.Path(__file__).parent.parent
    / "assets"
    / "validation"
    / "sample_ecr_config.yaml"
).read()


def test_organize_error_messages():
    # First just test a full set of messages
    # and include them all
    fatal = ["foo"]
    errors = ["my error1", "my_error2"]
    warns = ["my warn1"]
    infos = ["", "SOME"]
    test_include_errors = ["fatal", "errors", "warnings", "information"]
    msg_ids = {}

    expected_result = {
        "fatal": fatal,
        "errors": errors,
        "warnings": warns,
        "information": ["SOME"],
        "message_ids": msg_ids,
    }
    _clear_all_errors_and_ids()

    _append_error_message("fatal", fatal)
    _append_error_message("warnings", warns)
    _append_error_message("errors", errors)
    _append_error_message("information", infos)
    _add_message_ids(msg_ids)

    _organize_error_messages(include_error_types=test_include_errors)
    assert ERROR_MESSAGES == expected_result

    # Now, let's have full messages but only include 2 out of the 4
    # Should keep fatal ALWAYS and then the other 2 (errors and warnings)
    fatal = ["foo"]
    errors = ["my error1", "my_error2"]
    warns = ["my warn1"]
    infos = ["", "SOME"]
    test_include_errors = ["errors", "warnings"]
    msg_ids = {}

    expected_result = {
        "fatal": fatal,
        "errors": errors,
        "warnings": warns,
        "information": [],
        "message_ids": msg_ids,
    }
    _clear_all_errors_and_ids()
    _append_error_message("fatal", fatal)
    _append_error_message("warnings", warns)
    _append_error_message("errors", errors)
    _append_error_message("information", infos)
    _add_message_ids(msg_ids)

    _organize_error_messages(include_error_types=test_include_errors)
    assert ERROR_MESSAGES == expected_result

    # Now let's ensure that just information supplied
    # is picked up and filter out the '' message
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

    assert ERROR_MESSAGES == expected_result


def test_response_builder():
    # Test when the message is valid
    expected_response = {
        "message_valid": True,
        "validation_results": {
            "fatal": [],
            "errors": [],
            "warnings": [],
            "information": ["Validation completed with no fatal errors!"],
            "message_ids": {},
        },
    }
    _clear_all_errors_and_ids()

    actual_result = _response_builder(
        include_error_types=test_include_errors,
    )
    assert actual_result == expected_response

    # Now let's test when there is a fatal message
    #  should not be valid_message
    #  NOTE: Always need to clear the global ERROR_MESSAGE by
    #   calling the clear_all_errors_and_ids() function
    _clear_all_errors_and_ids()

    expected_response["validation_results"]["fatal"] = ["THIS IS A FATAL ERROR!"]
    expected_response["validation_results"]["information"] = []
    expected_response["message_valid"] = False

    _append_error_message("fatal", "THIS IS A FATAL ERROR!")

    actual_result = _response_builder(
        include_error_types=test_include_errors,
    )
    assert actual_result == expected_response


def test_append_error_message():
    _clear_all_errors_and_ids()
    # first let's test proper error message type
    #  with just a str error message with no spaces
    err_msg = "THIS IS AN ERROR"
    msg_ids = {}
    expected_result = {
        "fatal": [],
        "errors": [err_msg],
        "warnings": [],
        "information": [],
        "message_ids": msg_ids,
    }
    _append_error_message("errors", err_msg)

    assert ERROR_MESSAGES == expected_result

    _clear_all_errors_and_ids()
    # now let's test with an improper error message type
    # should all just be empty
    expected_result["errors"] = []
    _append_error_message("MY ERROR TYPE", err_msg)
    assert ERROR_MESSAGES == expected_result

    _clear_all_errors_and_ids()
    # now let's test with a proper error message type
    # and a message that is just spaces
    # should just return an empty 'errors'
    err_msg = "           "
    _append_error_message("errors", err_msg)
    assert ERROR_MESSAGES == expected_result

    _clear_all_errors_and_ids()
    # now let's test with a proper error message type
    # and two messages, one correct, and another that is just
    # spaces...should just return the correct one
    expected_result["errors"] = ["MY PROPER ERROR!"]
    err_msg = ["", "MY PROPER ERROR!", "     "]
    _append_error_message("errors", err_msg)
    assert ERROR_MESSAGES == expected_result

    _clear_all_errors_and_ids()
    # now let's test with a proper error message type
    # and two messages - should return both errors
    expected_result["errors"] = ["MY PROPER ERROR!", "YES AN ERROR!"]
    err_msg = [" MY PROPER ERROR!", "YES AN ERROR! "]
    _append_error_message("errors", err_msg)
    assert ERROR_MESSAGES == expected_result


def test_add_message_ids():
    _clear_all_errors_and_ids()
    # first let's test with a proper dict
    msg_ids = generate_ecr_msg_ids()
    expected_result = {
        "fatal": [],
        "errors": [],
        "warnings": [],
        "information": [],
        "message_ids": msg_ids,
    }
    _add_message_ids(ids=msg_ids)
    assert ERROR_MESSAGES == expected_result

    _clear_all_errors_and_ids()
    # now let's test with an empty dict
    msg_ids = {}
    expected_result = {
        "fatal": [],
        "errors": [],
        "warnings": [],
        "information": [],
        "message_ids": msg_ids,
    }
    _add_message_ids(ids=msg_ids)
    assert ERROR_MESSAGES == expected_result


def test_clear_all_errors_and_ids():
    # first let's load up all errors and msg ids
    #  and clear them out and make sure they are clear
    msg_ids = generate_ecr_msg_ids()
    fatal = ["foo"]
    errors = ["my error1", "my_error2"]
    warns = ["my warn1"]
    infos = ["", "SOME"]
    expected_result = {
        "fatal": [],
        "errors": [],
        "warnings": [],
        "information": [],
        "message_ids": {},
    }
    _add_message_ids(ids=msg_ids)
    _append_error_message("fatal", fatal)
    _append_error_message("warnings", warns)
    _append_error_message("errors", errors)
    _append_error_message("information", infos)
    assert ERROR_MESSAGES != expected_result
    _clear_all_errors_and_ids()
    assert ERROR_MESSAGES == expected_result
