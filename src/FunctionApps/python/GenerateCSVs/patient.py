from typing import List

PATIENT_COLUMNS = [
    "patientHash",
    "givenName",
    "familyName",
    "birthDate",
    "gender",
    "street",
    "city",
    "state",
    "postalCode",
    "latitude",
    "longitude",
    "race",
    "ethnicity",
    "standardizedFirstName",
    "standardizedLastName",
    "standardizedPhone",
    "standardizedAddress",
]


def parse_patient_resource(pt_rsc: dict) -> List[str]:
    """
    Given a FHIR patient resource, return a list whose form depends on whether or
    not we care about tracking metrics around standardization. If no, the form is:
    [<patientHash>,<givenName>,<familyName>,<birthDate>,<gender>,<street>,<city>,
    <state>,<postalCode>,<latitude>,<longitude>,<race>,<ethnicity>].

    If yes, then the form is as above, but with the following appended to the
    back of the list:
    [<firstNameWasStandardized>, <lastNameWasStandardized>,
    <phoneNumberWasStandardized>, <addressWasStandardized>]
    """
    patient_resource = (
        get_id(pt_rsc)
        + get_name(pt_rsc)
        + [pt_rsc["resource"].get("birthDate", "")]
        + [pt_rsc["resource"].get("gender", "")]
        + get_address(pt_rsc)
        + get_race_ethnicity(pt_rsc)
        + get_std_extensions(pt_rsc)
    )
    return patient_resource


def get_std_extensions(pt_rsc: dict) -> List[str]:
    """
    Given a patient resource, extract the information that identifies
    whether the fields that we run transformed on were "improved" in
    quality via standardization.
    """
    standardized_fields = {
        "first": "",
        "last": "",
        "phone": "",
        "address": "",
    }
    if "extension" in pt_rsc:
        for entry in pt_rsc["extension"]:
            entry_type = entry["url"].split("/")[-1]
            if entry_type == "family-name-was-standardized":
                standardized_fields["last"] = entry.get("valueBoolean")
            elif entry_type == "given-name-was-standardized":
                standardized_fields["first"] = entry.get("valueBoolean")
            elif entry_type == "phone-was-standardized":
                standardized_fields["phone"] = entry.get("valueBoolean")
            elif entry_type == "address-was-standardized":
                standardized_fields["address"] = entry.get("valueBoolean")
    return list(standardized_fields.values())


def get_id(pt_rsc: dict) -> List[str]:
    """Given a patient resource retrun a list containing the hashed identifier added
    previously in the PHDI pipeline."""

    hash = ""
    identifiers = pt_rsc["resource"].get("identifier")
    if identifiers:
        for id in identifiers:
            if id.get("system") == "urn:ietf:rfc:3986":
                hash = id.get("value")

    return [hash]


def get_name(pt_rsc: dict) -> List[str]:
    """Given a patient resource return a list of the form:[<givenName>, <familyName>].
    When present the first name designated as 'official' is used, otherwise the first
    name listed is used."""

    name_list = [""] * 2
    names = pt_rsc["resource"].get("name")
    if names:
        for name in names:
            if name.get("use") == "official":
                name_list = extract_name(name)
        if name_list == [""] * 2:
            name_list = extract_name(names[0])

    return name_list


def extract_name(name: dict) -> List[str]:
    """Given a an entry in the list of names from a patient resource return a list of
    the form [<first_name>,<last_name>]."""

    return [get_value(name, "given"), get_value(name, "family")]


def get_address(pt_rsc: dict) -> List[str]:
    """Given a patient resource return a list on the form:
    [<street>,<city>,<state>,<postalCode>,<latitude>,<longitude>].
    When present the first address designated as 'home' is used, otherwise the first
    address listed is used."""

    addr_list = [""] * 6
    addrs = pt_rsc["resource"].get("address")
    if addrs:
        for addr in addrs:
            if addr.get("use") == "home":
                addr_list = extract_address(addr)
        if addr_list == [""] * 6:
            addr_list = extract_address(addrs[0])

    return addr_list


def extract_address(addr: dict) -> List[str]:
    """Given a an entry in the list of addresses from a patient resource return a list
    of the form:
    [<street>,<city>,<state>,<postalCode>,<latitude>,<longitude>]."""

    addr_parts = ["line", "city", "state", "postalCode", "latitude", "longitude"]
    addr_list = []
    for part in addr_parts:
        if part not in ["latitude", "longitude"]:
            addr_list.append(get_value(addr, part))
        else:
            addr_list.append(get_coordinate(addr, part))

    return addr_list


def get_coordinate(addr: dict, coord: str) -> str:
    """Given an entry in the list of addresses from a patient resource return latitude
    or longitude (specified by coord) as a string."""

    value = ""
    if "extension" in addr:
        for extension in addr["extension"]:
            if (
                extension.get("url")
                == "http://hl7.org/fhir/StructureDefinition/geolocation"
            ):
                for coordinate in extension["extension"]:
                    if coordinate.get("url") == coord:
                        value = str(coordinate.get("valueDecimal"))

    return value


def get_race_ethnicity(pt_rsc: dict) -> List[str]:
    """Given a patient resource return the patient's race and ethnicity in a list of
    the form:[<race>,<ethnicity>]."""

    race = ""
    ethnicity = ""
    if "extension" in pt_rsc["resource"]:
        for extension in pt_rsc["resource"]["extension"]:
            if (
                extension["url"]
                == "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race"
            ):
                try:
                    race = extension["extension"][0]["valueCoding"]["code"]
                except KeyError:
                    race = ""
            elif (
                extension["url"]
                == "http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity"
            ):
                try:
                    ethnicity = extension["extension"][0]["valueCoding"]["code"]
                except KeyError:
                    ethnicity = ""

    return [race, ethnicity]


def get_value(dictionary: dict, key: str) -> str:
    """Given a dictionary and key return the value of the key. If the key is not present
    return an empty string. If the value is a list return the first element."""

    if key in dictionary:
        value = dictionary[key]
        if type(value) == list:
            value = value[0]
    else:
        value = ""

    return value
