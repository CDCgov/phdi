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
