import datetime
import pathlib
from typing import List
from typing import Literal
from typing import Union

import phonenumbers
import pycountry
from detect_delimiter import detect

from phdi.harmonization.double_metaphone import DoubleMetaphone

FHIR_DATE_FORMAT = "%Y-%m-%d"
FHIR_DATE_DELIM = "-"


def double_metaphone_string(string: str, dmeta=None) -> List[Union[str, None]]:
    """
    Performs the double metaphone phonetic encoding algorithm on the given
    string. Returns a list holding the primary and secondary phonetic
    representations of the string (including None if there is no valid
    secondary encoding). This function expects basic text cleaning (e.g.
    removal of numeric characters, trimming of spaces, etc.) to already
    have been performed.

    :param string: The string to phonetically encode.
    :param dmeta: An optional existing double metaphone object, in the case
      one has already been instantiated for bulk processing.
    :return: A list of the primary and secondary encodings of the given
      string.
    """
    if dmeta is None:
        dmeta = DoubleMetaphone()
    return dmeta(string)


def standardize_country_code(
    raw_country: str, code_type: Literal["alpha_2", "alpha_3", "numeric"] = "alpha_2"
) -> str:
    """
    Identifies the country represented and generates the desired type of the ISO
    3611 standardized country identifier for a given string representation of a country
    (whether a full name such as "United States," or an abbreviation such as "US"
    or "USA"). If the country identifier cannot be determined, returns None.

    Example: If raw_country = "United States of America," then

    * alpha_2 would be "US"
    * alpha_3 would be "USA"
    * numeric would be "840"

    :param raw_country: The string representation of the country to be
      put in ISO 3611 standardized form.
    :param code_type: One of 'alpha_2', 'alpha_3', or 'numeric'; the
      desired identifier type to generate.
    :return: The standardized country identifier found in the resource's addresses.
    """

    # @TODO: Potentially do some minor restructuring around this logic
    # to make it shorter/clearer. A private helper was discussed, but
    # prevailing consensus was that this logic is a guiding nice-to-have
    # here, where it is, so we'll likely keep it. But this todo marks
    # a revisit later around whether the logic can be restructuerd.

    # First, identify what country the input is referencing
    standard = None
    raw_country = raw_country.strip().upper()
    if len(raw_country) == 2:
        standard = pycountry.countries.get(alpha_2=raw_country)
    elif len(raw_country) == 3:
        standard = pycountry.countries.get(alpha_3=raw_country)
        if standard is None:
            standard = pycountry.countries.get(numeric=raw_country)
    elif len(raw_country) >= 4:
        standard = pycountry.countries.get(name=raw_country)
        if standard is None:
            standard = pycountry.countries.get(official_name=raw_country)

    # Then, if we figured that out, convert it to desired form
    if standard is not None:
        if code_type == "alpha_2":
            standard = standard.alpha_2
        elif code_type == "alpha_3":
            standard = standard.alpha_3
        elif code_type == "numeric":
            standard = standard.numeric

    return standard


def standardize_phone(
    raw_phone: Union[str, List[str]], countries: List = [None, "US"]
) -> Union[str, List[str]]:
    """
    Parses phone number and generates its standardized ISO E.164 international format
    for each given phone number and optional list of associated countries. If an input
    phone number can't be parsed, that number returns the empty string. Attempts
    to parse the inputs using the first successful strategy out of the following:

    1. parses the phone number on its own
    2. parses the phone number using the provided list of possible
       associated countries
    3. parses the phone number using the US as country

    :param raw_phone: One or more raw phone number(s) to standardize.
    :param countries: An optional list containing 2 letter ISO codes
      associated with the phone numbers, signifying to which countries
      the phone numbers might belong.
    :return: Either a string or a list of strings, depending on the
      input of raw_phone, holding the standardized phone number(s).
    """

    # Base cases: we always want to try the phone # on its own first;
    # we also want to try the phone # with the US if all else fails
    if None not in countries:
        countries.insert(0, None)
    if "US" not in countries:
        countries.append("US")

    phones_to_clean = raw_phone
    if isinstance(raw_phone, str):
        phones_to_clean = [raw_phone]
    outputs = []

    for phone in phones_to_clean:
        standardized = ""
        for country in countries:
            # We were able to pull the phone # and corresponding country
            try:
                standardized = phonenumbers.parse(phone, country)
                break

            # This combo of given phone # and country isn't valid
            except phonenumbers.phonenumberutil.NumberParseException:
                continue

        # If we got a match, format it according to ISO standards
        if standardized != "" and phonenumbers.is_possible_number(standardized):
            standardized = str(
                phonenumbers.format_number(
                    standardized, phonenumbers.PhoneNumberFormat.E164
                )
            )
            outputs.append(standardized)
        else:
            outputs.append("")

    if isinstance(raw_phone, str):
        return outputs[0]
    return outputs


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


def _build_nicknames_db():
    nicknames_to_names = {}
    with open(pathlib.Path(__file__).parent / "phdi_nicknames.csv", "r") as fp:
        for line in fp:
            if line.strip() != "":
                name, nicks = line.strip().split(":", 1)
                for nickname in nicks.split(","):
                    nicknames_to_names[nickname] = name
    return nicknames_to_names


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
        valid_date = datetime.datetime(int(year), int(month), int(day))
        if future and valid_date > datetime.datetime.now():
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
    param date_format: A python Date format used to parse and order
        the date components from the date string.
        Default: `%Y-%m-%d` (YYYY-MM-DD).
    :param future: A boolean that if True will verify that the date
        supplied is not in the future.
        Default: False
    :return: A date as a string in the FHIR Date Format.
    """
    # get the date delimiter from the date string
    # this is easier than regexp as we won't have to maintain a list
    # of potential delimiters and just look at what the delim is
    # for the date string supplied
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

    # verify that the date components in the date dictionary create a valid
    # date and based upon the future param that the date is not in the future
    if len(date_dict) != 3 or not _validate_date(
        date_dict["y"], date_dict["m"], date_dict["d"], future
    ):
        raise ValueError(f"Invalid date supplied: {raw_date}")

    return (
        date_dict["y"]
        + FHIR_DATE_DELIM
        + date_dict["m"]
        + FHIR_DATE_DELIM
        + date_dict["d"]
    )


def standardize_birth_date(
    raw_dob: str, existing_format: str = FHIR_DATE_FORMAT
) -> str:
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
