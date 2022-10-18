from app.config import get_settings


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


def search_for_required_values(input: dict, required_values: list) -> str:
    """
    Search for required values in the input dictionary and the environment.
    Found in the environment not present in the input dictionary that are found in the
    environment are added to the dictionary. A message is returned indicating which,
    if any, required values could not be found.

    :param input: A dictionary potentially originating from the body of a POST request
    :param required_values: A list of values to search for in the input dictionary and
    the environment.
    :return: A string message indicating if any required values could not be found and
    if so which ones.
    """

    missing_values = []

    for value in required_values:
        if input.get(value) in [None, ""]:
            if get_settings().get(value) is None:
                missing_values.append(value)
            else:
                input[value] = get_settings()[value]

    message = "All values were found."
    if missing_values != []:
        message = (
            "The following values are required, but were not included in the request "
            "and could not be read from the environment. Please resubmit the request "
            "including these values or add them as environment variables to this "
            f"service. missing values: {', '.join(missing_values)}."
        )

    return message
