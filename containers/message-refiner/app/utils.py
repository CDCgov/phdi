import json
import pathlib
from typing import List


def _generate_clinical_xpaths(system: str, codes: List[str]) -> List[str]:
    """
    This is a small helper function that loops through codes to create a set of
    xpaths that can be used in the refine step.

    :param system: This is the system type of the clinical service codes.
    :param codes: This is a list of the clinical service codes for a specified
    SNOMED code.
    """
    """
    As of May 2024, these are the code systems used in clinical services
    code_system
    http://snomed.info/sct                         28102
    http://loinc.org                                9509
    http://hl7.org/fhir/sid/icd-10-cm               5892
    http://www.nlm.nih.gov/research/umls/rxnorm      468
    http://hl7.org/fhir/sid/cvx                        2
    """
    system_dict = {
        "http://hl7.org/fhir/sid/icd-10-cm": "ICD10",
        "http://snomed.info/sct": "SNOMED CT",
        "http://loinc.org": "loinc.org",
        "http://www.nlm.nih.gov/research/umls/rxnorm": "?",  # TODO
        "http://hl7.org/fhir/sid/cvx": "?",  # TODO
    }

    # add condition to confirm if system in dict
    if system not in system_dict.keys():
        raise KeyError(f"{system} not a recognized clinical service system.")

    # Loop through each code and create the XPath expressions
    return [
        f".//*[local-name()='entry'][.//*[@code='{code}' and @codeSystemName='{system_dict.get(system)}']]"
        for code in codes
    ]


def create_clinical_xpaths(clinical_services_list: list[dict]) -> list[str]:
    """
    This function loops through each of those clinical service codes and their
    system to create a list of all possible xpath queries.
    :param clinical_services_list: List of clinical_service dictionaries.
    :return: List of xpath queries to check.
    """
    clinical_services_xpaths = []
    for clinical_services in clinical_services_list:
        for system, entries in clinical_services.items():
            for entry in entries:
                system = entry.get("system")
                xpaths = _generate_clinical_xpaths(system, entry.get("codes"))
                clinical_services_xpaths.extend(xpaths)
    return clinical_services_xpaths


def read_json_from_assets(filename: str) -> dict:
    """
    Reads a JSON file from the assets directory.

    :param filename: The name of the file to read.
    :return: A dictionary containing the contents of the file.
    """
    return json.load(open((pathlib.Path(__file__).parent.parent / "assets" / filename)))


def load_section_loincs(loinc_json: dict) -> tuple[list, dict]:
    """
    Reads section LOINC json to create two constants needed for parsing
    section data and creating refined sections.
    :param loinc_dict: Nested dictionary containing the nested section LOINCs
    :return: a list of all section LOINCs currently supported by the API;
             a dictionary of all required section LOINCs to pass validation
    """
    # LOINC codes for eICR sections our refiner API accepts
    section_list = list(loinc_json.keys())

    # dictionary of the required eICR sections'
    # LOINC code, displayName, templateId, extension, and title
    # to be used to create minimal sections and to support validation
    section_details = {
        loinc: details.get("minimal_fields")
        for loinc, details in loinc_json.items()
        if details.get("required")
    }
    return (section_list, section_details)
