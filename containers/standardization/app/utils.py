import copy
import json
import pathlib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Callable, Literal, List, Optional, Union

import phonenumbers
import pycountry
from detect_delimiter import detect
from fhirpathpy import evaluate as fhirpath_evaluate
from smartystreets_python_sdk import StaticCredentials, ClientBuilder, us_street
from smartystreets_python_sdk.us_street.lookup import Lookup


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


def standardize_phone(
    raw_phone: Union[str, List[str]], countries: List = [None, "US"]
) -> Union[str, List[str]]:
    """
    Parses phone number(s) and generates the standardized ISO E.164 international format
    for each given phone number as well as optional list of associated countries. If an
    input phone number can't be parsed, that number returns an empty string. Parsing
    uses the first successful strategy out of the following:

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


def _extract_countries_from_resource(
    resource: dict, code_type: Literal["alpha_2", "alpha_3", "numeric"] = "alpha_2"
) -> List[str]:
    """
    Builds a list containing all of the countries, standardized by code_type, in the
    addresses of a given FHIR resource as interpreted by the ISO 3611: standardized
    country identifier. If the resource is not of a supported type, no
    countries will be returned. Currently supported resource types are:

    * Patient

    :param resource: A FHIR resource or FHIR-formatted JSON dict.
    :param code_type: A string equal to 'alpha_2', 'alpha_3', or 'numeric'
      to specify which type of standard country identifier to generate.
      Default: `alpha_2`
    :return: A list of all the standardized countries found in the resource's
      addresses.
    """
    countries = []
    resource_type = resource.get("resourceType")
    if resource_type == "Patient":
        for address in resource.get("address"):
            country = address.get("country")
            if country:
                countries.append(standardize_country_code(country, code_type))
    return countries


def _standardize_phones_in_resource(
    resource: dict, overwrite=True
) -> Union[dict, None]:
    """
    Standardizes all phone numbers in a FHIR-formatted Patient resource.

    :param resource: A FHIR resource or FHIR-formatted JSON dict.
    :param overwrite: If true, `data` is modified in-place;
      if false, a copy of `data` modified and returned. Default: `True`.
    :return: The resource with phone numbers appropriately standardized.
    """
    if not overwrite:
        resource = copy.deepcopy(resource)

    if resource.get("resourceType", "") == "Patient":
        for telecom in resource.get("telecom", []):
            if telecom.get("system") == "phone" and "value" in telecom:
                countries = _extract_countries_from_resource(resource)
                transformed_phone = standardize_phone(
                    telecom.get("value", ""), countries
                )
                telecom["value"] = transformed_phone
    return resource


def standardize_phones_in_bundle(data: dict, overwrite=True) -> dict:
    """
    Standardizes all phone numbers in a given FHIR bundle or a FHIR resource.
    Standardization is done according to the underlying `standardize_phone`
    function in `phdi.harmonization`.

    :param data: A FHIR bundle or FHIR-formatted JSON dict.
    :param overwrite: If true, `data` is modified in-place;
      if false, a copy of `data` modified and returned.  Default: `True`
    :return: The bundle or resource with phones appropriately standardized.
    """

    if not overwrite:
        data = copy.deepcopy(data)

    # Allow users to pass in either a resource or a bundle
    bundle = data
    if "entry" not in data:
        bundle = {"entry": [{"resource": data}]}

    for entry in bundle.get("entry"):
        resource = entry.get("resource", {})
        resource = _standardize_phones_in_resource(resource, overwrite)

    if "entry" not in data:
        return bundle.get("entry", [{}])[0].get("resource", {})
    return bundle


@dataclass
class GeocodeResult:
    """
    Represents a successful geocoding response.
    Based on the field nomenclature of a FHIR address, specified at
    https://www.hl7.org/fhir/datatypes.html#Address.
    """

    line: List[str]
    city: str
    state: str
    postal_code: str
    county_fips: str
    lat: float
    lng: float
    district: Optional[str] = None
    country: Optional[str] = None
    county_name: Optional[str] = None
    precision: Optional[str] = None
    geoid: Optional[str] = None
    census_tract: Optional[str] = None
    census_block: Optional[str] = None


class BaseGeocodeClient(ABC):
    """
    Represents a vendor-agnostic geocoder client. Requires implementing
    classes to define methods to geocode from both strings and dictionaries.
    Callers should use the provided interface functions (e.g., geocode_from_str)
    to interact with the underlying vendor-specific client property.
    """

    @abstractmethod
    def geocode_from_str(self, address: str) -> Union[GeocodeResult, None]:
        """
        Geocodes the provided address, which is formatted as a string.

        :param address: The address to geocode, given as a string.
        :param overwrite: If true, `resource` is modified in-place;
          if false, a copy of `resource` modified and returned.  Default: `True`
        :return: A geocoded address (if valid result) or None (if no valid result).
        """
        pass  # pragma: no cover

    @abstractmethod
    def geocode_from_dict(self, address: dict) -> Union[GeocodeResult, None]:
        """
        Geocodes the provided address, which is formatted as a dictionary.

        The given dictionary should conform to standard nomenclature around address
        fields, including:

        * `street`: the number and street address
        * `street2`: additional street level information (if needed)
        * `apartment`: apartment or suite number (if needed)
        * `city`: city to geocode
        * `state`: state to geocode
        * `postal_code`: the postal code to use
        * `urbanization`: urbanization code for area, sector, or regional
        * `development`: (only used for Puerto Rican addresses)

        There is no minimum number of fields that must be specified to use this
        function; however, a minimum of street, city, and state are suggested
        for the best matches.

        :param address: A dictionary with fields outlined above.
        :return: A geocoded address (if valid result) or None (if no valid result).
        """
        pass  # pragma: no cover


class SmartyGeocodeClient(BaseGeocodeClient):
    """
    Represents a PHDI-supplied geocoding client using the Smarty API.
    Requires an authorization ID as well as an authentication token
    in order to build a street lookup client.
    """

    def __init__(
        self,
        smarty_auth_id: str,
        smarty_auth_token: str,
        licenses: list[str] = ["us-standard-cloud"],
    ):
        self.smarty_auth_id = smarty_auth_id
        self.smarty_auth_token = smarty_auth_token
        creds = StaticCredentials(smarty_auth_id, smarty_auth_token)
        self.__client = (
            ClientBuilder(creds).with_licenses(licenses).build_us_street_api_client()
        )

    @property
    def client(self) -> us_street.Client:
        """
        This property:
          1. defines a private instance variable __client
          2. makes it accessible through the use of .client()

        This property holds a Smarty-specific connection client that
        allows a user to geocode without directly referencing the
        underlying vendor service client.
        """
        return self.__client

    def geocode_from_str(self, address: str) -> Union[GeocodeResult, None]:
        """
        Geocodes the provided address, which is formatted as a string. If the
        result cannot be latitude- or longitude-located, then Smarty failed
        to precisely geocode the address, so no result is returned. Raises
        an error if the provided address is empty.

        :param address: The address to geocode, given as a string.
        :raises ValueError: When the address does not include street number and name.
        :return: A geocoded address (if valid result) or None (if no valid result).
        """

        # The smarty Lookup class will parse a BadRequestError but retry
        # 5 times if the lookup address is blank, so catch that here
        if address == "":
            raise ValueError("Address must include street number and name at a minimum")

        lookup = Lookup(street=address)
        self.__client.send_lookup(lookup)
        return self._parse_smarty_result(lookup)

    def geocode_from_dict(self, address: dict) -> Union[GeocodeResult, None]:
        """
        Geocodes the provided address, which is formatted as a dictionary.

        The given dictionary should conform to standard nomenclature around address
        fields, including:

        * `street`: the number and street address
        * `street2`: additional street level information (if needed)
        * `apartment`: apartment or suite number (if needed)
        * `city`: city to geocode
        * `state`: state to geocode
        * `postal_code`: the postal code to use
        * `urbanization`: urbanization code for area, sector, or regional
        * `development`: (only used for Puerto Rican addresses)

        There is no minimum number of fields that must be specified to use this
        function; however, a minimum of street, city, and state are suggested
        for the best matches.

        :param address: A dictionary with fields outlined above.
        :raises Exception: When the address street is an empty string.
        :return: A geocoded address (if valid result) or None (if no valid result).
        """

        # Smarty geocode requests must include a street level
        # field in the payload, otherwise generates BadRequestError
        if address.get("street", "") == "":
            raise ValueError("Address must include street number and name at a minimum")

        # Configure the lookup with whatever provided address values
        # were in the user-given dictionary
        lookup = Lookup()
        lookup.street = address.get("street", "")
        lookup.street2 = address.get("street2", "")
        lookup.secondary = address.get("apartment", "")
        lookup.city = address.get("city", "")
        lookup.state = address.get("state", "")
        lookup.zipcode = address.get("postal_code", "")
        lookup.urbanization = address.get("urbanization", "")
        lookup.match = "strict"

        self.__client.send_lookup(lookup)
        return self._parse_smarty_result(lookup)

    @staticmethod
    def _parse_smarty_result(lookup) -> Union[GeocodeResult, None]:
        """
        Parses a returned Smarty geocoding result into a GeocodeResult object.
        If the Smarty lookup is null or doesn't include latitude and longitude
        information, returns None instead.

        :param lookup: The us_street.lookup client instantiated for geocoding.
        :return: The geocoded address (if valid result) or None (if no valid result).
        """
        # Valid responses have results with lat/long
        if lookup.result and lookup.result[0].metadata.latitude:
            smartystreets_result = lookup.result[0]
            street_address = [smartystreets_result.delivery_line_1]
            if smartystreets_result.delivery_line_2:
                street_address.append(smartystreets_result.delivery_line_2)

            # Format the Smarty result into our standard dataclass object
            return GeocodeResult(
                line=street_address,
                city=smartystreets_result.components.city_name,
                state=smartystreets_result.components.state_abbreviation,
                postal_code=smartystreets_result.components.zipcode,
                county_fips=smartystreets_result.metadata.county_fips,
                county_name=smartystreets_result.metadata.county_name,
                lat=smartystreets_result.metadata.latitude,
                lng=smartystreets_result.metadata.longitude,
                precision=smartystreets_result.metadata.precision,
            )

        return
