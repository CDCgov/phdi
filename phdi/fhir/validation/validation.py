from phdi.validation.validation import validate_ecr


def validate_ecr_payload(ecr_message: str, error_types: list) -> dict:
    """
    Validates all fields in an eICR (ECR-CDA) message based upon a configuration
    that specifies which fiels are of interest including their format, their
    intented values within a valueset, and any related conditional fields.

    :param ecr_message: An eCR message, which is a CDA in XML format.
    :param error_types: A list of the errors types that should be included
        within the response of the validation (ie. error, warnings,
        information, etc...)
    :return: A response that contains if the validation was successful (true/false)
        as well as any individual errors/warnings that were indicated to include.
    """
    response = validate_ecr(
        ecr_message=ecr_message, config_path=None, error_types=error_types
    )
    return response
