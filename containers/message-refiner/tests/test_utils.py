import pytest
from app.utils import _generate_clinical_xpaths


def test_generate_clinical_xpath():
    """
    Confirms that xpaths can be generated for sample codes.
    """
    system = "http://loinc.org"
    codes = ["76078-5", "76080-1"]
    expected_output = [
        ".//*[local-name()='code'][@code='76078-5' and @codeSystemName='loinc.org']",
        ".//*[local-name()='value'][@code='76078-5' and @codeSystemName='loinc.org']",
        ".//*[local-name()='vaccine'][@code='76078-5' and @codeSystemName='loinc.org']",
        ".//*[local-name()='translation'][@code='76078-5' and @codeSystemName='loinc.org']",
        ".//*[local-name()='code'][@code='76080-1' and @codeSystemName='loinc.org']",
        ".//*[local-name()='value'][@code='76080-1' and @codeSystemName='loinc.org']",
        ".//*[local-name()='vaccine'][@code='76080-1' and @codeSystemName='loinc.org']",
        ".//*[local-name()='translation'][@code='76080-1' and @codeSystemName='loinc.org']",
    ]
    output = _generate_clinical_xpaths(system, codes)
    assert output == expected_output


def test_generate_clinical_xpaths_unknown_system():
    """
    Confirms error is generated if system is not recognized.
    """
    system = "http://unknown.org"
    codes = ["A01", "B02"]
    with pytest.raises(KeyError) as exc_info:
        _generate_clinical_xpaths(system, codes)
    assert (
        str(exc_info.value)
        == "'http://unknown.org not a recognized clinical service system.'"
    )
