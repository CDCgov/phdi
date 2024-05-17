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
        "http://loinc.org": "LOINC",
        "http://www.nlm.nih.gov/research/umls/rxnorm": "?",  # TODO
        "http://hl7.org/fhir/sid/cvx": "?",  # TODO
    }
    # XPath templates
    xpath_code = (
        "//*[local-name()='code'][@code='{code}' and @codeSystemName='{system}']"
    )
    xpath_vax = (
        "//*[local-name()='vaccine'][@code='{code}' and @codeSystemName='{system}']"
    )
    xpath_value = (
        "//*[local-name()='value'][@code='{code}' and @codeSystemName='{system}']"
    )
    xpath_translation = (
        "//*[local-name()='translation'][@code='{code}' and @codeSystemName='{system}']"
    )
    # Loop through each code and create the XPath expressions
    return [
        xpath.format(code=code, system=system_dict.get(system))
        for code in codes
        for xpath in [xpath_code, xpath_value, xpath_vax, xpath_translation]
    ]
