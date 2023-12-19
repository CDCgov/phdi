import copy
import json
import pathlib
from datetime import datetime
from typing import Dict, Callable, Literal, List, Union

from detect_delimiter import detect
from fhirpathpy import evaluate as fhirpath_evaluate


FHIR_DATE_FORMAT = "%Y-%m-%d"
FHIR_DATE_DELIM = "-"


def read_json_from_assets(filename: str):
    return json.load(open((pathlib.Path(__file__).parent.parent / "assets" / filename)))


def is_fhir_bundle(bundle) -> bool:
    """
    Check if the given data is a valid FHIR bundle.

    :param bundle: The data to check.
    :return: True if it's a FHIR bundle, False otherwise.
    """
    if not isinstance(bundle, dict):
        return False

    if bundle.get("resourceType") != "Bundle":
        return False

    entries = bundle.get("entry", [])
    if not isinstance(entries, list) or not all(
        "resource" in entry for entry in entries
    ):
        return False

    return True


def is_patient_resource(resource) -> bool:
    """
    Check if the given data is a valid FHIR patient resource.

    :param resource: The data to check.
    :return: True if it's a Patient resource, False otherwise.
    """
    return isinstance(resource, dict) and resource.get("resourceType") == "Patient"


def apply_function_to_fhirpath(bundle: Dict, fhirpath: str, function: Callable) -> Dict:
    """
    Applies a given function to elements in a FHIR bundle identified by a FHIRPath
    expression.

    :param bundle: A FHIR bundle.
    :param fhirpath: A FHIRPath expression to select elements in the resource.
    :param function: A function to be applied to each selected element.
    :return: The modified resource or bundle.
    """
    if not is_fhir_bundle(bundle):
        raise ValueError("The provided :param bundle is not a valid FHIR bundle.")

    elements = fhirpath_evaluate(bundle, fhirpath)

    for element in elements:
        # apply the function to each element
        function(element)

    return bundle


def standardize_name(
    raw_name: Union[str, List[str]],
    trim: bool = True,
    case: Literal["upper", "lower", "title"] = "upper",
    remove_numbers: bool = True,
) -> Union[str, List[str]]:
    """
    Performs basic standardization (described below) on each given name. Removes
    punctuation characters and performs a variety of additional cleaning operations.
    Other options can be toggled on or off using the relevant parameter.

    All options specified will be applied uniformly to each input name,
    i.e., specifying case = "lower" will make all given names lower case.

    :param raw_name: Either a single string name or a list of strings,
      each representing a name.
    :param trim: If true, strips leading/trailing whitespace;
      if false, retains whitespace. Default: `True`
    :param case: What case to enforce on each name.

      * `upper`: All upper case
      * `lower`: All lower case
      * `title`: Title case

      Default: `upper`
    :remove_numbers: If true, removes numeric characters from inputs;
      if false, retains numeric characters. Default `True`
    :return: Either a string or a list of strings, depending on the
      input of raw_name, holding the cleaned name(s).
    """
    names_to_clean = raw_name
    if isinstance(raw_name, str):
        names_to_clean = [raw_name]
    outputs = []

    for name in names_to_clean:
        # Remove all punctuation
        cleaned_name = "".join([ltr for ltr in name if ltr.isalnum() or ltr == " "])
        if remove_numbers:
            cleaned_name = "".join([ltr for ltr in cleaned_name if not ltr.isnumeric()])
        if trim:
            cleaned_name = cleaned_name.strip()
        if case == "upper":
            cleaned_name = cleaned_name.upper()
        if case == "lower":
            cleaned_name = cleaned_name.lower()
        if case == "title":
            cleaned_name = cleaned_name.title()
        outputs.append(cleaned_name)

    if isinstance(raw_name, str):
        return outputs[0]
    return outputs


def _validate_date(year: str, month: str, day: str, future: bool = False) -> bool:
    """
    Validates that a date supplied, split out by the different date components
        is a valid date (ie. not 02-30-2000 or 12-32-2000). This function can
        also verify that the date supplied is not greater than now

    :param raw_date: One date in string format to standardize.
    :param existing_format: A python DateTime format used to parse the date
        supplied.  Default: `%Y-%m-%d` (YYYY-MM-DD).
    :param new_format: A python DateTime format used to convert the date
        supplied into.  Default: `%Y-%m-%d` (YYYY-MM-DD).
    :return: A date as a string in the format supplied by new_format.
    """
    is_valid_date = True
    try:
        valid_date = datetime(int(year), int(month), int(day))
        if future and valid_date > datetime.now():
            is_valid_date = False
    except ValueError:
        is_valid_date = False

    return is_valid_date


def _standardize_date(
    raw_date: str, date_format: str = FHIR_DATE_FORMAT, future: bool = False
) -> str:
    """
    Validates a date string is a proper date and then standardizes the
    date string into the FHIR Date Standard (YYYY-MM-DD)

    :param raw_date: A date string to standardize.
    :param date_format: A python Date format used to parse and order
        the date components from the date string.
        Default: `%Y-%m-%d` (YYYY-MM-DD).
    :param future: A boolean that if True will verify that the date
        supplied is not in the future.
        Default: False
    :return: A date as a string in the FHIR Date Format.
    """
    # TODO: detect function from detect-delimiter hasn't been updated
    # since 2018; might be worth replacing with a more robust library
    # or writing our own detection function
    delim = detect(raw_date)
    format_delim = detect(date_format.replace("%", ""))

    # parse out the different date components (year, month, day)
    date_values = raw_date.split(delim)
    format_values = date_format.replace("%", "").lower().split(format_delim)
    date_dict = {}

    # loop through date values and the format values
    #   and create a date dictionary where the format is the key
    #   and the date values are the value ordering the date component values
    #   using the date format supplied
    for format_value, date_value in zip(format_values, date_values):
        date_dict[format_value[0]] = date_value

    # check that all the necessary date components are present within the date_dict
    if not all(key in date_dict for key in ["y", "m", "d"]):
        raise ValueError(
            f"Invalid date format or missing components in date: {raw_date}"
        )

    # verify that the date components in the date dictionary create a valid
    # date and based upon the future param that the date is not in the future
    if not _validate_date(date_dict["y"], date_dict["m"], date_dict["d"], future):
        raise ValueError(f"Invalid date format supplied: {raw_date}")

    return (
        date_dict["y"]
        + FHIR_DATE_DELIM
        + date_dict["m"]
        + FHIR_DATE_DELIM
        + date_dict["d"]
    )


def standardize_dob(raw_dob: str, existing_format: str = FHIR_DATE_FORMAT) -> str:
    """
    Validates and standardizes a date of birth string into YYYY-MM-DD format.

    :param raw_dob: One date of birth (dob) to standardize.
    :param existing_format: A python DateTime format used to parse the date of
        birth within the Patient resource.  Default: `%Y-%m-%d` (YYYY-MM-DD).
    :return: Date of birth as a string in YYYY-MM-DD format
        or None if date of birth is invalid.
    """
    #  Need to make sure dob is not None or null ("")
    #  or detect() will end up in an infinite loop
    if raw_dob is None or len(raw_dob) == 0:
        raise ValueError("Date of Birth must be supplied!")

    standardized_dob = _standardize_date(
        raw_date=raw_dob, date_format=existing_format, future=True
    )

    return standardized_dob


def standardize_dob_fhir(
    data: Dict, date_format: str = "%Y-%m-%d", overwrite: bool = True
) -> Dict:
    """
    Standardizes all birth dates in a given FHIR bundle or a FHIR patient resource.
    Standardization is done according to the 'standardize_dob' function.
    The final birthDate will follow the FHIR STu3/R4 format of YYYY-MM-DD.

    :param data: A FHIR bundle or FHIR patient resource.
    :param date_format: A python DateTime format used to parse the birthDate.
                        Default: '%Y-%m-%d' (YYYY-MM-DD).
    :param overwrite: If true, `data` is modified in-place;
                      if false, a copy of `data` is modified and returned.
                      Default: True.
    :return: The modified bundle or patient resource.
    """
    if not overwrite:
        data = copy.deepcopy(data)

    if is_fhir_bundle(data):
        fhirpath = "Bundle.entry.resource.where(resourceType='Patient').birthDate"
    elif is_patient_resource(data):
        fhirpath = "Patient.birthDate"
    else:
        raise ValueError(
            "The provided data is neither a valid FHIR Bundle nor a Patient resource."
        )

    def standardize_dob_in_element(element):
        if "value" in element:
            element["value"] = standardize_dob(element["value"], date_format)

    return apply_function_to_fhirpath(data, fhirpath, standardize_dob_in_element)
