import pathlib
from unittest.mock import patch

import pytest
from app.main import app
from app.main import refine
from app.main import select_message_header
from app.main import validate_message
from app.main import validate_sections_to_include
from app.utils import _generate_clinical_xpaths
from fastapi.testclient import TestClient
from lxml import etree as ET

client = TestClient(app)


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

mock_tcr_response = {
    "lrtc": [{"codes": ["76078-5", "76080-1"], "system": "http://loinc.org"}]
}


def test_health_check():
    actual_response = client.get("/")
    assert actual_response.status_code == 200
    assert actual_response.json() == {"status": "OK"}


def test_ecr_refiner():
    # Test case: sections_to_include = None
    expected_response = parse_file_from_test_assets("CDA_eICR.xml")
    content = test_eICR_xml
    sections_to_include = None
    endpoint = "/ecr/"
    actual_response = client.post(endpoint, content=content)
    assert actual_response.status_code == 200

    actual_flattened = [i.tag for i in ET.fromstring(actual_response.content).iter()]
    expected_flattened = [i.tag for i in expected_response.iter()]
    assert actual_flattened == expected_flattened

    # Test case: sections_to_include = "29762-2" # social history narrative
    expected_response = refined_test_eICR_social_history_only
    content = test_eICR_xml
    sections_to_include = "29762-2"
    endpoint = f"/ecr/?sections_to_include={sections_to_include}"
    actual_response = client.post(endpoint, content=content)
    assert actual_response.status_code == 200

    actual_flattened = [i.tag for i in ET.fromstring(actual_response.content).iter()]
    expected_flattened = [i.tag for i in expected_response.iter()]
    assert actual_flattened == expected_flattened

    # Test case: sections_to_include = "30954-2,29299-5" # labs/diagnostics and reason for visit
    expected_response = refined_test_eICR_labs_reason
    content = test_eICR_xml
    sections_to_include = "30954-2,29299-5"
    endpoint = f"/ecr/?sections_to_include={sections_to_include}"
    actual_response = client.post(endpoint, content=content)
    assert actual_response.status_code == 200
    actual_flattened = [i.tag for i in ET.fromstring(actual_response.content).iter()]
    expected_flattened = [i.tag for i in expected_response.iter()]
    assert actual_flattened == expected_flattened

    # Test case: sections_to_include is invalid
    expected_response = "blah blah blah is invalid. Please provide a valid section."
    content = test_eICR_xml
    sections_to_include = "blah blah blah"
    endpoint = f"/ecr/?sections_to_include={sections_to_include}"
    actual_response = client.post(endpoint, content=content)
    assert actual_response.status_code == 422
    assert actual_response.content.decode() == expected_response

    # Test case: raw_message is invalid XML
    content = "invalid XML"
    sections_to_include = None
    endpoint = "/ecr/"
    actual_response = client.post(endpoint, content=content)
    assert actual_response.status_code == 400
    assert "XMLSyntaxError" in actual_response.content.decode()


@patch("requests.get")
def test_ecr_refiner_conditions(mock_get):
    # Mock the response from the trigger-code-reference service
    mock_get.return_value.json.return_value = mock_tcr_response
    # Test conditions only
    expected_response = refined_test_condition_only
    content = test_eICR_xml
    conditions_to_include = "6142004"
    endpoint = f"/ecr/?conditions_to_include={conditions_to_include}"
    actual_response = client.post(endpoint, content=content)
    assert actual_response.status_code == 200
    assert actual_response.content.decode() == expected_response

    actual_elements = [
        i.tag.split("}")[-1] for i in ET.fromstring(actual_response.content).iter()
    ]
    assert "ClinicalDocument" in actual_elements

    # Test conditions and sections
    content = test_eICR_xml
    expected_response = refined_test_conditon_and_labs
    sections_to_include = "30954-2"
    conditions_to_include = "6142004"
    endpoint = f"/ecr/?sections_to_include={sections_to_include}&conditions_to_include={conditions_to_include}"
    actual_response = client.post(endpoint, content=content)
    assert actual_response.status_code == 200
    assert actual_response.content.decode() == expected_response

    actual_elements = [
        i.tag.split("}")[-1] for i in ET.fromstring(actual_response.content).iter()
    ]
    assert "ClinicalDocument" in actual_elements

    # Test conditions but no relevant section
    content = test_eICR_xml
    expected_response = refined_test_no_relevant_section_data
    conditions_to_include = "6142004"
    sections_to_include = "46240-8"
    endpoint = f"/ecr/?sections_to_include={sections_to_include}&conditions_to_include={conditions_to_include}"
    actual_response = client.post(endpoint, content=content)
    assert actual_response.status_code == 200
    assert actual_response.content.decode() == expected_response

    actual_elements = [
        i.tag.split("}")[-1] for i in ET.fromstring(actual_response.content).iter()
    ]
    assert "ClinicalDocument" in actual_elements


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
            (None, "blah blah blah is invalid. Please provide a valid section."),
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
    expected_flattened = [i.tag for i in ET.fromstring(expected_message).iter()]
    assert actual_flattened == expected_flattened

    # Test case: Refine for condition and labs/diagnostics section
    expected_message = refined_test_conditon_and_labs
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
    actual_header = select_message_header(raw_message)
    expected_header = test_header
    actual_flattened = [i.tag for i in actual_header.iter()]
    expected_flattened = [i.tag for i in expected_header.iter()]
    assert actual_flattened == expected_flattened


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
