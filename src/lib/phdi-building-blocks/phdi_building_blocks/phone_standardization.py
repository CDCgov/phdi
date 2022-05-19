from phdi_building_blocks.utils import find_patient_resources
from typing import Callable


def standardize_phone(raw: str) -> str:
    """Make sure it's 10 digits, remove everything else

    >>> standardize_phone("(555) 555-1212")
    '5555551212'
    """

    raw = [x for x in raw if x.isnumeric()]
    raw = "".join(raw)
    if len(raw) != 10:
        raw = None
    return raw


def standardize_patient_phone(
    bundle: dict, standardize: Callable = standardize_phone
) -> dict:
    """Given a FHIR bundle and a standardization function, standardize the phone numbers
    in all patient resources in the bundle. By default the standardize_phone function
    defined in this module is used, but the user is free to provide their own function
    specifying a standardization process as long as it accepts and returns a string."""

    for resource in find_patient_resources(bundle):
        patient = resource.get("resource")
        if "extension" not in patient:
            patient["extension"] = []
        # Transform phone numbers
        raw_phones = []
        std_phones = []
        for telecom in patient.get("telecom", []):
            if telecom.get("system") == "phone" and "value" in telecom:
                transformed_phone = standardize(telecom["value"])
                raw_phones.append(telecom["value"])
                std_phones.append(transformed_phone)
                telecom["value"] = transformed_phone
        any_diffs = len(raw_phones) != len(std_phones) or any(
            [raw_phones[i] != std_phones[i] for i in range(len(raw_phones))]
        )
        patient["extension"].append(
            {
                "url": "http://usds.gov/fhir/phdi/StructureDefinition/phone-was-standardized",  # noqa
                "valueBoolean": any_diffs,
            }
        )
    return bundle
