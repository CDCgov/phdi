import os


def check_for_fhir(value: dict) -> dict:
    """
    Check if the value provided is a valid FHIR resource or bundle by asserting that
    a 'resourceType' key exists with a non-null value.

    :param value: Dictionary to be tested for FHIR validity.
    :return: The dictionary originally passed in as 'value'
    """

    assert value.get("resourceType") not in [
        None,
        "",
    ], "Must provide a FHIR resource or bundle"
    return value


def check_for_fhir_bundle(value: dict) -> dict:
    """
    Check if the dictionary provided is a valid FHIR bundle by asserting that a
    'resourceType' key exists with the value 'Bundle'.

    :param value: Dictionary to be tested for FHIR validity.
    :return: The dictionary originally passed in as 'value'
    """

    assert (
        value.get("resourceType") == "Bundle"
    ), "Must provide a FHIR resource or bundle"  # noqa
    return value


def check_for_environment_variables(environment_variables: list) -> dict:
    """
    Check that all environment variables in a given list are set.

    :param environment_variables: A list of environment variables to check.
    :return: A dictionary containing two keys: 'status_code' and 'message'.
        'status_code' has value of 200 when all environment variables are found, and 500
        when one or more are missing. 'message' is a string identifying the first
        missing environment variable or indicating that all specified variables were
        found.
    """
    for environment_variable in environment_variables:
        if os.environ.get(environment_variable) is None:
            error_message = (
                "Environment variable '{}' not set. "
                + "The environment variable must be set."
            ).format(environment_variable)
            return {"status_code": 500, "message": error_message}

    return {"status_code": 200, "message": "All environment variables were found."}
