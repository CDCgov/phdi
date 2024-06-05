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


def read_json_from_assets(filename: str) -> dict:
    """
    Reads a JSON file from the assets directory.

    :param filename: The name of the file to read.
    :return: A dictionary containing the contents of the file.
    """
    return json.load(open((pathlib.Path(__file__).parent.parent / "assets" / filename)))
