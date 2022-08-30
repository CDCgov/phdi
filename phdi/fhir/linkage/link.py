import copy
from phdi.fhir.utils import (
    find_resource_by_type,
    get_field,
    get_one_line_address,
)
from phdi.linkage.link import generate_hash_str


def add_patient_identifier_by_bundle(
    bundle: dict, salt_str: str, overwrite: bool = True
) -> dict:
    """
    Given a FHIR resource bundle:

    * identify all patient resource(s) in the bundle
    * add the hash string to the list of identifiers held in that patient resource

    :param bundle: The FHIR bundle for whose patients to add a
        linking identifier
    :param salt_str: The suffix string added to prevent being
        able to reverse the hash into PII
    :param overwrite: Whether to write the new standardizations
        directly into the given bundle, changing the original data (True
        is yes)
    """
    if not overwrite:
        bundle = copy.deepcopy(bundle)

    for resource in find_resource_by_type(bundle, "Patient"):
        add_patient_identifier(resource, salt_str, overwrite)
    return bundle


def add_patient_identifier(resource, salt_str, overwrite):
    """
    Given a FHIR resource:

    * extract name, DOB, and address information for each
    * compute a unique hash string based on these fields
    * add the hash string to resource

    :param resource: The FHIR patient resource to add a
        linking identifier
    :param salt_str: The suffix string added to prevent being
        able to reverse the hash into PII
    :param overwrite: Whether to write the new standardizations
        directly into the given bundle, changing the original data (True
        is yes)
    """
    if not overwrite:
        resource = copy.deepcopy(resource)
    patient = resource.get("resource")

    # Combine given and family name
    recent_name = get_field(patient, "name", "official", 0)
    name_parts = recent_name.get("given", []) + [recent_name.get("family", "")]
    name_str = "-".join([n for n in name_parts if n])

    address_line = ""
    if "address" in patient:
        address = get_field(patient, "address", "home", 0)
        address_line = get_one_line_address(address)

    # TODO Determine if minimum quality criteria should be included, such as min
    # number of characters in last name, valid birth date, or address line
    # Generate and store unique hash code
    link_str = f'{name_str}-{patient["birthDate"]}-{address_line}'
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
    return patient
