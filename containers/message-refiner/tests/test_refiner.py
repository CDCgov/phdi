import pathlib

import pytest
from app.main import app
from app.main import refine
from app.main import validate_sections_to_include
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
        tree = ET.parse(
            file,
            parser,
        )
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


def test_health_check():
    actual_response = client.get("/")
    assert actual_response.status_code == 200
    assert actual_response.json() == {
        "status": "OK",
    }


def test_ecr_refiner():
    # Test case: sections_to_include = None
    expected_response = test_eICR_xml
    content = test_eICR_xml
    sections_to_include = None
    endpoint = "/ecr/"
    actual_response = client.post(endpoint, content=content)
    assert actual_response.status_code == 200
    assert actual_response.content.decode() == expected_response

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
    raw_message = test_eICR_xml
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
    raw_message = test_eICR_xml
    refined_message = refine(raw_message, sections_to_include)

    actual_flattened = [i.tag for i in ET.fromstring(refined_message).iter()]
    expected_flattened = [i.tag for i in expected_message.iter()]
    assert actual_flattened == expected_flattened
