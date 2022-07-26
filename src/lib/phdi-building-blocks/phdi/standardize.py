import phonenumbers
import pycountry
from typing import Literal, List
from phdi_building_blocks.utils import (
    find_resource_by_type,
    standardize_text,
)
import copy


def standardize_patient_names(
    bundle: dict,
    trim: bool = True,
    case: Literal["upper", "lower", "title"] = "upper",
    remove_numbers: bool = True,
    overwrite: bool = True,
) -> dict:
    """
    Given a FHIR bundle and a type of standardization to perform,
    transform all names in all patients in the bundle. The default
    standardization behavior is our defined non-numeric, space-trimming,
    full capitalization standardization, but other modes may be specified.

    :param bundle: The FHIR bundle to standardize patients in
    :param trim: Indicates if leading and trailing whitespace should be removed.
    :param: case: Specifies the casing that should be used for the name.
    :param: remove_numbers: Indicates if numbers should be removed from the name.
    :param overwrite: Indicates whether the original data should be overwritten with
    the transformed values.
    """
    # Copy the data if we don't want to overwrite the original
    if not overwrite:
        bundle = copy.deepcopy(bundle)

    # Handle all patients individually
    for resource in find_resource_by_type(bundle, "Patient"):
        patient = resource.get("resource")
        standardize_names_for_patient(
            patient, trim=trim, case=case, remove_numbers=remove_numbers
        )

    return bundle


# TODO In some functions, like standardize_patient_names, we return a bundle, and in
# other places we don't. We should standardize this across the code to make it easier
# to read.
def standardize_names_for_patient(patient: dict, **kwargs) -> None:
    """
    Helper method to standardize all names associated with a single patient.
    Receives a particular standardization function from the calling method
    standardize_patient_names. Default behavior is to use the simple
    non-numeric, space-trimming, full capitalization standardization.

    :param patient: The Patient resource to standardize all names for
    :param transform_func: The particular standardization function
        to invoke for these transforms
    """

    for name in patient.get("name", []):

        # Handle family names
        if "family" in name:
            transformed_name = standardize_text(name.get("family", ""), **kwargs)
            name["family"] = transformed_name

        # Given names are stored in a list, as there could be multiple,
        # process them all and take the overall diff for metrics
        if "given" in name:
            transformed_names = [
                standardize_text(g, **kwargs) for g in name.get("given", [])
            ]
            name["given"] = transformed_names

    return None


def extract_countries_from_resource(
    resource: dict, code_type: Literal["alpha_2", "alpha_3", "numeric"] = "alpha_2"
) -> List[str]:
    """
    Given a FHIR resource, build a list containing all of the counries found in the
    addresses associated with that resource in a standardized form sepcified by
    code_type.

    :param resource: A patient from a FHIR resource
    :param code_type: A string equal to 'alpha_2', 'alpha_3', or 'numeric' to
        specify which type of standard country identifier to generate
    """
    countries = []
    resource_type = resource.get("resource").get("resourceType")
    if resource_type == "Patient":
        for address in resource.get("resource").get("address"):
            country = address.get("country")
            countries.append(standardize_country(country, code_type))
    return countries


def standardize_phone(raw: str, countries: List = [None, "US"]) -> str:
    """
    Given a phone number and optionally an associated FHIR resource and country
    extraction function if able to parse the phone number return it in the E.164
    standardard international format. If the phone number is not parseable return none.

    Phone number parsing process:
    A maximum of three attemtps are made to parse any phone number.
    First, we try to parse the phone number without any additional country information.
    If this succeeds then the phone number must have been provided in a standard
    inernational format which is the ideal case. If the first attempt fails and a list
    of country codes indicating possible countries of origin for the phone number has
    been provided we attempt to parse the phone number using that additional country
    information from the resource. Finally, in the case where the second attempt fails
    or a list of countries has not been provided we make a final attempt to parse the
    number assuming it is American.

    :param raw: Raw phone number to be standardized.
    :param countries: A list containing 2 letter ISO country codes for each country
        extracted from resource of the phone number to be standardized that might
        indicate it the phone numbers country of origin.
    """

    if countries != [None, "US"]:
        countries = [None] + countries + ["US"]

    standardized = ""
    for country in countries:
        try:
            standardized = phonenumbers.parse(raw, country)
            break
        except phonenumbers.phonenumberutil.NumberParseException:
            continue
    if standardized != "":
        standardized = str(
            phonenumbers.format_number(
                standardized, phonenumbers.PhoneNumberFormat.E164
            )
        )
    return standardized


def standardize_country(
    raw: str, code_type: Literal["alpha_2", "alpha_3", "numeric"] = "alpha_2"
) -> str:
    """
    Given a country return it in a standard form as specified by code_type.

    :param raw: Country to be standardized.
    :param code_type: A string equal to 'alpha_2', 'alpha_3', or 'numeric' to
        specify which type of standard country identifier to generate.
    """
    standard = None
    raw = raw.strip().upper()
    if len(raw) == 2:
        standard = pycountry.countries.get(alpha_2=raw)
    elif len(raw) == 3:
        standard = pycountry.countries.get(alpha_3=raw)
        if standard is None:
            standard = pycountry.countries.get(numeric=raw)
    elif len(raw) >= 4:
        standard = pycountry.countries.get(name=raw)
        if standard is None:
            standard = pycountry.countries.get(official_name=raw)

    if standard is not None:
        if code_type == "alpha_2":
            standard = standard.alpha_2
        elif code_type == "alpha_3":
            standard = standard.alpha_3
        elif code_type == "numeric":
            standard = standard.numeric

    return standard


def standardize_all_phones(
    bundle: dict,
    overwrite: bool = True,
) -> dict:
    """
    Given a FHIR bundle and a type of phone number standardization,
    transform all phone numberes for all patient resources in the
    bundle.

    :param bundle: The FHIR bundle to standardize patients in
    :param overwrite: Whether to overwrite the original data
        with the transformed values. Default is yes.
    """
    if not overwrite:
        bundle = copy.deepcopy(bundle)

    for patient in find_resource_by_type(bundle, "Patient"):
        standardize_phone_numbers_for_patient(patient)

    return bundle


def standardize_phone_numbers_for_patient(
    patient_resource: dict,
) -> None:
    """
    Helper method to standardize all phone numbers in a single patient
    resource using the caller-supplied transformation function.

    :param patient: The patient to standardize all numbers for
    """
    for telecom in patient_resource.get("resource").get("telecom", []):
        if telecom.get("system") == "phone" and "value" in telecom:
            countries = extract_countries_from_resource(patient_resource)
            transformed_phone = standardize_phone(telecom.get("value", ""), countries)
            telecom["value"] = transformed_phone

    return None
