import pathlib
import re

import pytest
from app.refine import _add_root_element
from app.refine import _create_minimal_section
from app.refine import _create_minimal_sections
from app.refine import _select_message_header
from app.refine import refine
from app.refine import validate_message
from app.refine import validate_sections_to_include
from app.utils import _generate_clinical_xpaths
from app.utils import load_section_loincs
from app.utils import read_json_from_assets
from lxml import etree as ET


def parse_file_from_test_assets(filename: str) -> ET.ElementTree:
    """
    Parses a file from the assets directory into an ElementTree.

    :param filename: The name of the file to read.
    :return: An ElementTree containing the contents of the file.
    """
    with open(
        (pathlib.Path(__file__).parent.parent / "tests" / "assets" / filename), "r"
    ) as file:
        parser = ET.XMLParser(remove_blank_text=True)
        tree = ET.parse(file, parser)
        return tree


def read_file_from_test_assets(filename: str) -> str:
    """
    Reads a file from the assets directory.

    :param filename: The name of the file to read.
    :return: A string containing the contents of the file.
    """
    with open(
        (pathlib.Path(__file__).parent.parent / "tests" / "assets" / filename),
        "r",
    ) as file:
        return file.read()


test_eICR_xml = read_file_from_test_assets("CDA_eICR.xml")
refined_test_eICR_social_history_only = parse_file_from_test_assets(
    "refined_message_social_history_only.xml"
)
refined_test_eICR_labs_reason = parse_file_from_test_assets(
    "refined_message_labs_reason.xml"
)

refined_test_condition_only = parse_file_from_test_assets(
    "refined_message_condition_only.xml"
)

refined_test_conditon_and_labs = parse_file_from_test_assets(
    "refined_message_condition_and_lab_section.xml"
)

refined_test_no_relevant_section_data = parse_file_from_test_assets(
    "refined_message_with_condition_and_section_with_no_condition_info.xml"
)

test_header = parse_file_from_test_assets("test_header.xml")


@pytest.mark.parametrize(
    "test_data, expected_result",
    [
        # Test case: single sections_to_include
        (
            "29762-2",
            (["29762-2"], ""),
        ),
        # Test case: multiple sections_to_include
        (
            "10164-2,29299-5",
            (["10164-2", "29299-5"], ""),
        ),
        # Test case: no sections_to_include
        (
            None,
            (None, ""),
        ),
        # Test case: invalid sections_to_include
        (
            "blah blah blah",
            ([], "blah blah blah is invalid. Please provide a valid section."),
        ),
    ],
)
def test_validate_sections_to_include(test_data, expected_result):
    # # Test cases: single and multiple sections_to_include
    if test_data != "blah blah blah" and test_data is not None:
        actual_response = validate_sections_to_include(test_data)
        assert actual_response == expected_result
        assert isinstance(actual_response[0], list)
    # Test case: no sections_to_include
    elif test_data is None:
        actual_response = validate_sections_to_include(test_data)
        assert actual_response == expected_result
        assert actual_response[0] is None
    # Test case: invalid sections_to_include
    else:
        actual_response = validate_sections_to_include(test_data)
        assert actual_response == expected_result
        assert actual_response[1] != ""


def test_refine():
    raw_message = ET.fromstring(test_eICR_xml)
    # Test case: Refine for only social history
    expected_message = refined_test_eICR_social_history_only
    sections_to_include = ["29762-2"]
    refined_message = refine(raw_message, sections_to_include)

    actual_flattened = [i.tag for i in ET.fromstring(refined_message).iter()]
    expected_flattened = [i.tag for i in expected_message.iter()]
    assert actual_flattened == expected_flattened

    # Test case: Refine for labs/diagnostics and reason for visit
    expected_message = refined_test_eICR_labs_reason
    sections_to_include = ["30954-2", "29299-5"]
    raw_message = ET.fromstring(test_eICR_xml)
    refined_message = refine(raw_message, sections_to_include)

    actual_flattened = [i.tag for i in ET.fromstring(refined_message).iter()]
    expected_flattened = [i.tag for i in expected_message.iter()]
    assert actual_flattened == expected_flattened

    # Test case: Refine for condition only
    expected_message = refined_test_condition_only
    raw_message = ET.fromstring(test_eICR_xml)
    system = "http://loinc.org"
    codes = ["76078-5", "76080-1"]
    mock_clinical_service_xpaths = _generate_clinical_xpaths(system, codes)
    refined_message = refine(
        raw_message,
        sections_to_include=None,
        clinical_services=mock_clinical_service_xpaths,
    )
    actual_flattened = [i.tag for i in ET.fromstring(refined_message).iter()]
    expected_flattened = [i.tag for i in expected_message.iter()]
    assert actual_flattened == expected_flattened

    # Test case: Refine for condition and labs/diagnostics section
    expected_message = refined_test_conditon_and_labs
    raw_message = ET.fromstring(test_eICR_xml)
    sections_to_include = ["30954-2"]
    refined_message = refine(
        raw_message,
        sections_to_include=sections_to_include,
        clinical_services=mock_clinical_service_xpaths,
    )
    actual_flattened = [i.tag for i in ET.fromstring(refined_message).iter()]
    expected_flattened = [i.tag for i in expected_message.iter()]
    assert actual_flattened == expected_flattened


def test_select_header():
    raw_message = ET.fromstring(test_eICR_xml)
    actual_header = _select_message_header(raw_message)
    expected_header = test_header
    actual_flattened = [i.tag for i in actual_header.iter()]
    expected_flattened = [i.tag for i in expected_header.iter()]
    assert actual_flattened == expected_flattened


def test_add_root_element():
    raw_message = ET.fromstring(test_eICR_xml)
    header = _select_message_header(raw_message)
    elements = raw_message.xpath(
        "//*[local-name()='section']", namespaces={"hl7": "urn:hl7-org:v3"}
    )
    result = _add_root_element(header, elements)
    # TODO: I could only get this to work with regex
    assert re.sub(r"\s+", "", result) == re.sub(r"\s+", "", test_eICR_xml)


def test_validate_message():
    # Test case: valid XML
    raw_message = test_eICR_xml
    actual_response, error_message = validate_message(raw_message)
    actual_flattened = [i.tag for i in actual_response.iter()]
    expected_flattened = [i.tag for i in ET.fromstring(raw_message).iter()]
    assert actual_flattened == expected_flattened
    assert error_message == ""

    # Test case: invalid XML
    raw_message = "this is not a valid XML"
    actual_response, error_message = validate_message(raw_message)
    assert actual_response is None
    assert "XMLSyntaxError" in error_message


_, SECTION_DETAILS = load_section_loincs(read_json_from_assets("section_loincs.json"))


def test_create_minimal_section():
    # Test case: Valid section code, not empty
    section_code = "29762-2"
    empty_section = False
    result = _create_minimal_section(section_code, empty_section)
    assert result is not None
    assert result.tag == "section"
    assert result.find("templateId").get("root") == "2.16.840.1.113883.10.20.22.2.17"
    assert result.find("templateId").get("extension") == "2015-08-01"
    assert result.find("code").get("code") == section_code
    assert result.find("code").get("displayName") == "Social History"
    assert result.find("title").text == "Social History"
    assert "nullFlavor" not in result.attrib
    assert (
        "Only entries that match the corresponding condition code were included"
        in result.find("text").text
    )

    # Test case: Valid section code, empty
    empty_section = True
    result = _create_minimal_section(section_code, empty_section)
    assert result is not None
    assert result.tag == "section"
    assert result.get("nullFlavor") == "NI"
    assert (
        "Removed via PRIME DIBBs Message Refiner API endpoint"
        in result.find("text").text
    )

    # Test case: Invalid section code
    section_code = "invalid-code"
    result = _create_minimal_section(section_code, empty_section)
    assert result is None


def test_create_minimal_sections():
    # Test case: No sections to include or conditions
    result = _create_minimal_sections()
    assert len(result) == len(SECTION_DETAILS)  # all minimal
    assert all([section.tag == "section" for section in result])
    assert all([section.get("nullFlavor") == "NI" for section in result])

    # Test case: Sections to include
    sections_to_include = ["29762-2"]
    result = _create_minimal_sections(sections_to_include=sections_to_include)
    expected_length = len(SECTION_DETAILS) - len(sections_to_include)
    assert len(result) == expected_length  # Excluded section should be minimal

    # Check that excluded sections are in the result
    excluded_sections = set(SECTION_DETAILS.keys()) - set(sections_to_include)
    assert all(
        [section.find("code").get("code") in excluded_sections for section in result]
    )

    # Test case: Sections with conditions
    sections_with_conditions = ["30954-2"]
    result = _create_minimal_sections(sections_with_conditions=sections_with_conditions)
    expected_length = len(SECTION_DETAILS) - len(sections_with_conditions)
    assert len(result) == expected_length  # Excluded section should be minimal

    # Check that excluded sections are in the result
    excluded_sections = set(SECTION_DETAILS.keys()) - set(sections_with_conditions)
    assert all(
        [section.find("code").get("code") in excluded_sections for section in result]
    )

    # Test case: Sections to include and sections with conditions
    sections_to_include = ["29762-2"]
    sections_with_conditions = ["30954-2"]
    result = _create_minimal_sections(
        sections_to_include=sections_to_include,
        sections_with_conditions=sections_with_conditions,
    )
    expected_length = (
        len(SECTION_DETAILS) - len(sections_to_include) - len(sections_with_conditions)
    )
    assert len(result) == expected_length  # Excluded sections should be minimal

    # Check that excluded sections are in the result
    excluded_sections = (
        set(SECTION_DETAILS.keys())
        - set(sections_to_include)
        - set(sections_with_conditions)
    )
    assert all(
        [section.find("code").get("code") in excluded_sections for section in result]
    )

    # Test case: Empty sections
    result = _create_minimal_sections(empty_section=False)
    assert len(result) == len(SECTION_DETAILS)  # Should create minimal sections for all
    assert all([section.tag == "section" for section in result])
    assert all(["nullFlavor" not in section.attrib for section in result])
