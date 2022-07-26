import hashlib
import copy
from phdi_building_blocks.utils import (
    find_resource_by_type,
    get_one_line_address,
    get_field,
)


def add_patient_identifier(bundle: dict, salt_str: str, overwrite: bool = True) -> dict:
    """
    Given a FHIR resource bundle:

    * identify all patient resource(s) in the bundle
    * extract name, DOB, and address information for each
    * compute a unique hash string based on these fields
    * add the hash string to the list of identifiers held in that patient resource

    :param bundle: The FHIR bundle for whose patients to add a
        linking identifier
    :param salt_str: The suffix string added to prevent being
        able to reverse the hash into PII
    :param overwrite: Whether to write the new standardizations
        directly into the given bundle, changing the original data (True
        is yes)
    """
    # Copy the data if we don't want to overwrite the original
    if not overwrite:
        bundle = copy.deepcopy(bundle)

    for resource in find_resource_by_type(bundle, "Patient"):
        patient = resource.get("resource")

        # Combine given and family name
        recent_name = get_field(patient, "name", "official", 0)
        name_parts = recent_name.get("given", []) + [recent_name.get("family", "")]
        name_str = "-".join([n for n in name_parts if n])

        # Compile one-line address string
        address_line = ""
        if "address" in patient:
            address = get_field(patient, "address", "home", 0)
            address_line = get_one_line_address(address)

        # TODO Determine if minimum quality criteria should be included, such as min
        # number of characters in last name, valid birth date, or address line
        # Generate and store unique hash code
        link_str = name_str + "-" + patient["birthDate"] + "-" + address_line
        hashcode = generate_hash_str(link_str, salt_str)

        if "identifier" not in patient:
            patient["identifier"] = []

        # TODO Follow up on the validity and source of the comment about the system
        # value corresponding to the FHIR specification. Need to either add a citation
        # or correct the wording to more properly reflect what it represents.
        patient["identifier"].append(
            {
                "value": hashcode,
                # Note: this system value corresponds to the FHIR specification
                # for a globally used / generated ID or UUID--the standard here
                # is to make the use "temporary" even if it's not
                "system": "urn:ietf:rfc:3986",
                "use": "temp",
            }
        )

    return bundle


def generate_hash_str(linking_identifier: str, salt_str: str) -> str:
    """
    Given a string made of concatenated patient information, generate
    a hash for this string to serve as a "unique" identifier for the
    patient.

    :param linking_identifier: The concatenation of a patient's name,
        address, and date of birth, delimited by dashes
    :param salt_str: The salt to concatenate onto the end to prevent
        being able to reverse-engineer PII
    """
    hash_obj = hashlib.sha256()
    to_encode = (linking_identifier + salt_str).encode("utf-8")
    hash_obj.update(to_encode)
    return hash_obj.hexdigest()
