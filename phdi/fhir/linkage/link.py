import copy

from phdi.fhir.utils import find_entries_by_resource_type
from phdi.fhir.utils import get_field
from phdi.fhir.utils import get_one_line_address
from phdi.linkage.link import generate_hash_str


def add_patient_identifier_in_bundle(
    bundle: dict, salt_str: str, overwrite: bool = True
) -> dict:
    """
    Given a FHIR resource bundle:

    * Identifies all patient resource(s) in the bundle
    * Adds the hash string to the list of identifiers held in that patient resource

    :param bundle: The FHIR bundle for whose patients to add a linking identifier.
    :param salt_str: The salt to use with the hash. This is intended to prevent
      reverse engineering of the PII used to create the hash.
    :param overwrite: If true, `bundle` is modified in-place;
      if false, a copy of `bundle` modified and returned.  Default: `True`
    :return: The bundle, resources updated with additional patient identifier.
    """
    if not overwrite:
        bundle = copy.deepcopy(bundle)

    for entry in find_entries_by_resource_type(bundle, "Patient"):
        patient = entry.get("resource")
        add_patient_identifier(patient, salt_str)
    return bundle


def add_patient_identifier(
    patient_resource: dict, salt_str: str, overwrite: bool = True
):
    """
    Given a FHIR Patient resource:

    * Extracts name, DOB, and address information
    * Computes a unique hash string based on these fields
    * Adds the hash string to resource

    :param patient_resource: The FHIR patient resource to add a linking identifier.
    :param salt_str: The salt to use with the hash. This is intended to prevent
      reverse engineering of the PII used to create the hash.
    :param overwrite: If true, `patient_resource` is modified in-place;
      if false, a copy of `patient_resource` modified and returned.  Default: `True`
    :return: The resource updated with additional patient identifier.
    """
    if not overwrite:
        patient_resource = copy.deepcopy(patient_resource)

    # Combine given and family name
    recent_name = (
        get_field(patient_resource, field="name", use="official", require_use=False)
        or {}
    )
    name_parts = recent_name.get("given", []) + [recent_name.get("family", "")]
    name_str = "-".join([n for n in name_parts if n])

    address_line = ""
    if "address" in patient_resource:
        address = (
            get_field(patient_resource, field="address", use="home", require_use=False)
            or {}
        )
        address_line = get_one_line_address(address)

    # TODO Determine if minimum quality criteria should be included, such as min
    # number of characters in last name, valid birth date, or address line
    # Generate and store unique hash code
    link_str = f'{name_str}-{patient_resource["birthDate"]}-{address_line}'
    hashcode = generate_hash_str(link_str, salt_str)

    if "identifier" not in patient_resource:
        patient_resource["identifier"] = []

    # TODO Follow up on the validity and source of the comment about the system
    # value corresponding to the FHIR specification. Need to either add a citation
    # or correct the wording to more properly reflect what it represents.
    patient_resource["identifier"].append(
        {
            "value": hashcode,
            # Note: this system value corresponds to the FHIR specification
            # for a globally used / generated ID or UUID--the standard here
            # is to make the use "temporary" even if it's not
            "system": "urn:ietf:rfc:3986",
            "use": "temp",
        }
    )
    return patient_resource
