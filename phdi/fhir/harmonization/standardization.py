import copy
from typing import List
from typing import Literal
from typing import Union

from phdi.harmonization import double_metaphone_string
from phdi.harmonization import DoubleMetaphone
from phdi.harmonization import standardize_birth_date
from phdi.harmonization import standardize_country_code
from phdi.harmonization import standardize_name
from phdi.harmonization import standardize_phone


def double_metaphone_bundle(bundle: dict, overwrite=True) -> dict:
    """
    Performs the double metaphone algorithm on each name of each patient in a
    given FHIR bundle.

    :param bundle: A FHIR bundle of data containing one or more patient
      resources.
    :param overwrite: If true, `data` is modified in-place; if false, a
      copy of `data` modified and returned.  Default: `True`.
    :return: A dictionary mapping the FHIR IDs of patients in the bundle
      to lists holding the double metaphone representations of their
      names for each FHIR use case their resource includes.
    """
    if not overwrite:
        bundle = copy.deepcopy(bundle)

    dmeta = DoubleMetaphone()
    for entry in bundle.get("entry", []):
        resource = entry.get("resource", {})
        if resource.get("resourceType", "") == "Patient":
            double_metaphone_patient(resource, dmeta, overwrite=True)
    return bundle


def double_metaphone_patient(patient: dict, dmeta=None, overwrite=True) -> dict:
    """
    Performs the double metaphone algorithm for each name in a given patient
    resource. The algorithm is performed on each component of the name (first,
    middle, last), and the resulting representations are ordered in a list
    such that the first element is first name, the last element is last name,
    and all other elements are one or more middle names in the order of
    name presentation. These lists of phonetic representations are stored as
    the values of dictionaries whose keys are the FHIR uses of the name in
    the patient resource (e.g. "official"), and all such dictionaries are
    returned to the caller in a list ordered the same as the names within
    the given resource.

    :param patient: A FHIR-formatted JSON dictionary representing a patient
      resource.
    :param dmeta: An optional existing instantiation of a double metaphone
      object for use in bulk processing.
    :param overwrite: If true, `data` is modified in-place; if false, a
      copy of `data` modified and returned.  Default: `True`.
    :return: A list of dictionaries mapping FHIR uses to the phonetic
      representations of names associated with those uses, in presentation
      order (first, middle, last).
    """

    if not overwrite:
        patient = copy.deepcopy(patient)

    for name in patient.get("name", []):
        # Processing last name separately allows us to note in the result
        # whether last name wasn't present ( = [None, None])
        dm_last = double_metaphone_string(name.get("family", ""), dmeta)
        dm_givens = []

        # Each name is processed sequentially because FHIR expects given
        # names to already follow proper presentation order
        for given in name.get("given", []):
            dm_givens.append(double_metaphone_string(given, dmeta))

        # Cleanest way to store computed encodings is as an extension directly
        # within the HumanName objects of the patient's `name` field
        if name.get("extension", []) == []:
            name["extension"] = []

        name.get("extension").append(
            {
                "url": "https://xlinux.nist.gov/dads/HTML/doubleMetaphone.html",
                "extension": [
                    {"url": "familyName", "valueString": dm_last},
                    {"url": "givenName", "valueString": dm_givens},
                ],
            }
        )

    return patient


def standardize_names(
    data: dict,
    trim: bool = True,
    case: Literal["upper", "lower", "title"] = "upper",
    remove_numbers: bool = True,
    overwrite: bool = True,
) -> dict:
    """
    Standardizes all names contained in a given FHIR bundle or a FHIR resource. The
    default standardization behavior is our defined non-numeric, space-trimming, full
    capitalization standardization, but other modes may be specified.

    :param data: A FHIR-formatted JSON dict.
    :param trim: Whether leading/trailing whitespace should be removed. Default: `True`
    :param case: The type of casing that should be used. Default: `upper`
    :param remove_numbers: If true, delete numeric characters; if false leave numbers
      in place. Default: `True`
    :param overwrite: If true, `data` is modified in-place;
      if false, a copy of `data` modified and returned.  Default: `True`
    :return: The bundle or resource with names appropriately standardized.
    """
    # Copy the data if we don't want to overwrite the original
    if not overwrite:
        data = copy.deepcopy(data)

    # Allow users to pass in either a resource or a bundle
    bundle = data
    if "entry" not in data:
        bundle = {"entry": [{"resource": data}]}

    # Handle all resources individually
    for entry in bundle.get("entry"):
        resource = entry.get("resource", {})
        resource = _standardize_names_in_resource(
            resource, trim, case, remove_numbers, overwrite
        )

    if "entry" not in data:
        return bundle.get("entry", [{}])[0].get("resource", {})
    return bundle


def standardize_phones(data: dict, overwrite=True) -> dict:
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


def _standardize_names_in_resource(
    resource: dict,
    trim: bool = True,
    case: Literal["upper", "lower", "title"] = "upper",
    remove_numbers: bool = True,
    overwrite: bool = True,
) -> dict:
    """
    Standardizes all found names in a given resource.
    The resource can be of any type currently supported by the
    function's logic. At this time, those resources include:

    * Patient

    The parameters to this function match the standardization flags
    used by the underlying `standardize_name` function found in
    `phdi.harmonization`. For more information, see the docstring for
    that function.

    :param resource: A FHIR-formatted JSON dictionary.
    :param trim: Whether leading/trailing whitespace should be removed.
      Default: `True`
    :param case: The type of casing that should be used. Default: `upper`
    :param remove_numbers: Whether to delete numeric characters.
      Default: `True`
    :param overwrite: Whether to replace the original names in the input
      data with the standardized names. Default: `True`
    :return: The resource with appropriately standardized names.
    """

    if not overwrite:
        resource = copy.deepcopy(resource)

    if resource.get("resourceType", "") == "Patient":
        for name in resource.get("name", []):
            # Handle family names
            if "family" in name:
                transformed_name = standardize_name(
                    name.get("family", ""), trim, case, remove_numbers
                )
                name["family"] = transformed_name

            # Given names are stored in a list, as there could be multiple,
            # process them all and take the overall diff for metrics
            if "given" in name:
                transformed_names = [
                    standardize_name(g, trim, case, remove_numbers)
                    for g in name.get("given", [])
                ]
                name["given"] = transformed_names
    return resource


def _standardize_phones_in_resource(
    resource: dict, overwrite=True
) -> Union[dict, None]:
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


def _extract_countries_from_resource(
    resource: dict, code_type: Literal["alpha_2", "alpha_3", "numeric"] = "alpha_2"
) -> List[str]:
    """
    Builds a list containing all of the countries, standardized by code_type, in the
    addresses of a given FHIR resource as interpreted by the ISO 3611: standardized
    country identifier. If the resource is not of a supported type, no
    countries will be returned. Currently supported resource types are:

    * Patient

    :param resource: A FHIR-formatted JSON dictionary.
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


def _standardize_dob_in_resource(
    resource: dict, format: str = "%Y-%m-%d", overwrite=True
) -> Union[dict, None]:
    if not overwrite:
        resource = copy.deepcopy(resource)

    if resource.get("resourceType", "") == "Patient":
        birth_date = resource.get("birthDate")
        transformed_birth_date = standardize_birth_date(birth_date, format)
        resource["birthDate"] = transformed_birth_date
    return resource


def standardize_dob(data: dict, format: str = "%Y-%m-%d", overwrite=True) -> dict:
    """
    Standardizes all birth dates in a given FHIR bundle or a FHIR resource.
    Standardization is done according to the underlying `standardize_dob` function in
    `phdi.harmonization`.  The final birthDate will follow the FHIR STu3/R4 format
    of YYYY-MM-DD which will be stored in the Patient resource.

    :param data: A FHIR bundle or FHIR-formatted JSON dict.
    :param format: A python DateTime format used to parse the birthDate within
      the Patient resource.  Default: `%Y-%m-%d` (also known as YYYY-MM-DD)
    :param overwrite: If true, `data` is modified in-place;
      if false, a copy of `data` modified and returned.  Default: `True`
    :return: The bundle or resource with bith dates appropriately standardized.
    """

    if not overwrite:
        data = copy.deepcopy(data)

    # Allow users to pass in either a resource or a bundle
    bundle = data
    if "entry" not in data:
        bundle = {"entry": [{"resource": data}]}

    for entry in bundle.get("entry"):
        resource = entry.get("resource", {})
        resource = _standardize_dob_in_resource(resource, format, overwrite)

    if "entry" not in data:
        return bundle.get("entry", [{}])[0].get("resource", {})
    return bundle
