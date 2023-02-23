import pathlib
from phdi.validation.validation import validate_ecr


# Test file with known errors
sample_file_bad = open(
    pathlib.Path(__file__).parent.parent / "assets" / "ecr_sample_input_bad.xml"
).read()


# Test good file
sample_file_good = open(
    pathlib.Path(__file__).parent.parent / "assets" / "ecr_sample_input_good.xml"
).read()

config_path = pathlib.Path(__file__).parent.parent / "assets" / "sample_ecr_config.yaml"


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
        config_path=config_path,
        error_types=["error", "warn", "info"],
    )

    assert result == expected_response


def test_validate_bad():
    expected_response = {
        "message_valid": False,
        "validation_results": {
            "errors": [
                "Could not find attribute value for tag eICR Version Number",
                "Field: Zip does not match regEx: [0-9]{5}(?:-[0-9]{4})?",
            ],
            "warnings": [],
            "information": [],
        },
    }
    result = validate_ecr(
        ecr_message=sample_file_bad,
        config_path=config_path,
        error_types=["error", "warn", "info"],
    )

    assert result == expected_response
