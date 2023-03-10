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

# Test good file with RR data
sample_file_good_RR = open(
    pathlib.Path(__file__).parent.parent
    / "assets"
    / "ecr_sample_input_good_with_RR.xml"
).read()

# Test config file with custom error messages
with open(
    pathlib.Path(__file__).parent.parent
    / "assets"
    / "sample_ecr_config_custom_messages.yaml",
    "r",
) as file2:
    config_with_custom_errors = yaml.safe_load(file2)


# standard config file
with open(
    pathlib.Path(__file__).parent.parent / "assets" / "sample_ecr_config.yaml", "r"
) as file:
    config = yaml.safe_load(file)

# standard config file with correct RR Data
with open(
    pathlib.Path(__file__).parent.parent / "assets" / "sample_ecr_config_with_rr.yaml",
    "r",
) as file:
    config_rr = yaml.safe_load(file)


def test_validate_good():
    eicr_result = {
        "root": "2.16.840.1.113883.9.9.9.9.9",
        "extension": "db734647-fc99-424c-a864-7e3cda82e704",
    }
    rr_result = {}
    expected_response = {
        "message_valid": True,
        "validation_results": {
            "fatal": [],
            "errors": [],
            "warnings": [],
            "information": ["Validation completed with no fatal errors!"],
            "message_ids": {"eicr": eicr_result, "rr": rr_result},
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
    expected_response = {
        "message_valid": False,
        "validation_results": {
            "fatal": [
                "Could not find field. Field name: 'eICR Version Number' Attributes:"
                + " name: 'value'",
                "Could not find field. Field name: 'First Name' Parent element: 'name'"
                + " Parent attributes: name: 'use' RegEx: 'L'",
                "Could not find field. Field name: 'City' Parent element: 'addr' Parent"
                + " attributes: name: 'use' RegEx: 'H'",
                "Field does not match regEx: [0-9]{5}(?:-[0-9]{4})?. Field name:"
                + " 'Zip' value: '9999'",
            ],
            "errors": [],
            "warnings": [
                "Attribute: 'code' not in expected format. Field name: 'Sex'"
                + " Attributes: name: 'code' RegEx: 'F|M|O|U' value: 't', name:"
                + " 'codeSystem' value: '2.16.840.1.113883.5.1'"
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
                "Could not find attribute code. Field name: 'Status' Attributes: name:"
                + " 'code'",
                "Could not find attribute code. Field name: 'Status' Attributes: name:"
                + " 'code'",
            ],
            "warnings": [],
            "information": ["Validation completed with no fatal errors!"],
            "message_ids": {
                "eicr": {
                    "root": "2.16.840.1.113883.9.9.9.9.9",
                    "extension": "db734647-fc99-424c-a864-7e3cda82e704",
                },
                "rr": {},
            },
        },
        "validated_message": sample_file_error,
    }
    result = validate_ecr(
        ecr_message=sample_file_error,
        config=config,
        include_error_types=test_include_errors,
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
            "message_ids": {},
        },
        "validated_message": None,
    }
    result = validate_ecr(
        ecr_message=" BLAH ",
        config=config,
        include_error_types=test_include_errors,
    )
    assert result == expected_response


def test_custom_error_messages():
    expected_result = {
        "message_valid": True,
        "validation_results": {
            "errors": ["Invalid postal code"],
            "fatal": [],
            "warnings": [],
            "information": ["Validation completed with no fatal errors!"],
            "message_ids": {
                "eicr": {
                    "root": "2.16.840.1.113883.9.9.9.9.9",
                    "extension": "db734647-fc99-424c-a864-7e3cda82e704",
                },
                "rr": {},
            },
        },
        "validated_message": sample_file_bad,
    }
    result = validate_ecr(
        ecr_message=sample_file_bad,
        config=config_with_custom_errors,
        include_error_types=test_include_errors,
    )
    assert expected_result == result


def test_validate_good_with_rr_data():
    eicr_result = {
        "root": "2.16.840.1.113883.9.9.9.9.9",
        "extension": "db734647-fc99-424c-a864-7e3cda82e704",
    }
    rr_result = {
        "root": "4efa0e5c-c34c-429f-b5de-f1a13aef4a28",
        "extension": None,
    }
    expected_response = {
        "message_valid": True,
        "validation_results": {
            "fatal": [],
            "errors": [],
            "warnings": [],
            "information": ["Validation completed with no fatal errors!"],
            "message_ids": {"eicr": eicr_result, "rr": rr_result},
        },
        "validated_message": sample_file_good_RR,
    }
    result = validate_ecr(
        ecr_message=sample_file_good_RR,
        config=config_rr,
        include_error_types=test_include_errors,
    )
    assert result == expected_response


def test_validate_with_rr_data_missing_rr():
    eicr_result = {
        "root": "2.16.840.1.113883.9.9.9.9.9",
        "extension": "db734647-fc99-424c-a864-7e3cda82e704",
    }

    expected_response = {
        "message_valid": False,
        "validation_results": {
            "fatal": [
                "Could not find field. Field name: 'Status' Attributes: name: 'code' RegEx: 'RRVS19|RRVS20|RRVS21|RRVS22', name: 'codeSystem', name: 'displayName'",
                "Could not find field. Field name: 'Conditions' Attributes: name: 'code' RegEx: '[0-9]+', name: 'codeSystem'",
            ],
            "errors": [],
            "warnings": [],
            "information": [],
            "message_ids": {"eicr": eicr_result, "rr": {}},
        },
        "validated_message": None,
    }
    result = validate_ecr(
        ecr_message=sample_file_good,
        config=config_rr,
        include_error_types=test_include_errors,
    )
    print(result["validation_results"])
    print(expected_response["validation_results"])
    assert result == expected_response
