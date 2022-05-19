from phdi_building_blocks.utils import find_patient_resources
from typing import Callable


def standardize_name(raw: str) -> str:
    """trim spaces and force uppercase

    >>> standardize_name(" JohN Doe ")
    'JOHN DOE'
    """

    raw = [x for x in raw if not x.isnumeric()]
    raw = "".join(raw)
    raw = raw.upper()
    raw = raw.strip()
    return raw


def standardize_patient_name(
    bundle: dict, standardize: Callable = standardize_name
) -> dict:
    """Given a FHIR bundle and a standardization function, standardize the patient names
    in all patient resources in the bundle. By default the standardize_name function
    defined in this module is used, but the user is free to provide their own function
    specifying a standardization process as long as it accepts and returns a string."""

    for resource in find_patient_resources(bundle):
        patient = resource.get("resource")
        if "extension" not in patient:
            patient["extension"] = []

        # Transform names
        for name in patient.get("name", []):
            if "family" in name:
                std_family = standardize(name["family"])
                raw_family = name["family"]
                patient["extension"].append(
                    {
                        "url": "http://usds.gov/fhir/phdi/StructureDefinition/family-name-was-standardized",  # noqa
                        "valueBoolean": raw_family != std_family,
                    }
                )
                name["family"] = std_family

            if "given" in name:
                std_givens = [standardize(g) for g in name["given"]]
                raw_givens = [g for g in name["given"]]
                any_diffs = any(
                    [raw_givens[i] != std_givens[i] for i in range(len(raw_givens))]
                )
                patient["extension"].append(
                    {
                        "url": "http://usds.gov/fhir/phdi/StructureDefinition/given-name-was-standardized",  # noqa
                        "valueBoolean": any_diffs,
                    }
                )
                name["given"] = std_givens

    return bundle


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
