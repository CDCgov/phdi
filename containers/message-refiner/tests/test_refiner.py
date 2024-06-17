import json
import pathlib
from unittest.mock import AsyncMock
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from app.main import app
from app.main import get_clinical_services
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


def test_get_uat_collection():
    uat_collection = json.load(
        open(
            pathlib.Path(__file__).parent.parent
            / "assets"
            / "Message_Refiner_UAT.postman_collection.json"
        )
    )
    actual_response = client.get("example-collection")
    assert actual_response.status_code == 200
    assert actual_response.json() == uat_collection


def test_openapi():
    actual_response = client.get("/message-refiner/openapi.json")
    assert actual_response.status_code == 200


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


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get", new_callable=AsyncMock)
async def test_ecr_refiner_conditions(mock_get):
    # Mock the response from the trigger-code-reference service
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_tcr_response
    mock_get.return_value = mock_response

    # Test conditions only
    expected_response = refined_test_condition_only
    content = test_eICR_xml
    conditions_to_include = "6142004"
    endpoint = f"/ecr/?conditions_to_include={conditions_to_include}"
    actual_response = client.post(endpoint, content=content)
    assert actual_response.status_code == 200

    actual_flattened = [
        i.tag for i in ET.fromstring(actual_response.content.decode()).iter()
    ]
    expected_flattened = [i.tag for i in expected_response.iter()]
    assert actual_flattened == expected_flattened
    actual_elements = [
        i.tag.split("}")[-1]
        for i in ET.fromstring(actual_response.content.decode()).iter()
    ]
    assert "ClinicalDocument" in actual_elements

    # Test conditions and relevant labs section
    expected_response = refined_test_conditon_and_labs
    content = test_eICR_xml
    conditions_to_include = "6142004"
    sections_to_include = "30954-2"
    endpoint = f"/ecr/?sections_to_include={sections_to_include}&conditions_to_include={conditions_to_include}"
    actual_response = client.post(endpoint, content=content)
    assert actual_response.status_code == 200

    actual_flattened = [
        i.tag for i in ET.fromstring(actual_response.content.decode()).iter()
    ]
    expected_flattened = [i.tag for i in expected_response.iter()]
    assert actual_flattened == expected_flattened
    actual_elements = [
        i.tag.split("}")[-1]
        for i in ET.fromstring(actual_response.content.decode()).iter()
    ]
    assert "ClinicalDocument" in actual_elements

    # Test conditions, history of hospitalization section without relevant data
    expected_response = refined_test_no_relevant_section_data
    content = test_eICR_xml
    conditions_to_include = "6142004"
    sections_to_include = "46240-8"
    endpoint = f"/ecr/?sections_to_include={sections_to_include}&conditions_to_include={conditions_to_include}"
    actual_response = client.post(endpoint, content=content)
    assert actual_response.status_code == 200

    actual_flattened = [
        i.tag for i in ET.fromstring(actual_response.content.decode()).iter()
    ]
    expected_flattened = [i.tag for i in expected_response.iter()]
    assert actual_flattened == expected_flattened
    actual_elements = [
        i.tag.split("}")[-1]
        for i in ET.fromstring(actual_response.content.decode()).iter()
    ]
    assert "ClinicalDocument" in actual_elements


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get", new_callable=AsyncMock)
async def test_get_clinical_services(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "lrtc": [{"codes": ["76078-5", "76080-1"], "system": "http://loinc.org"}]
    }
    mock_get.return_value = mock_response

    condition_codes = "6142004"
    clinical_services = await get_clinical_services(condition_codes)
    expected_result = [mock_response]
    assert clinical_services == expected_result


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get", new_callable=AsyncMock)
async def test_get_clinical_services_error(mock_get):
    mock_response = Mock()
    mock_response.status_code = 503
    mock_response.json.return_value = {"detail": "Not Found"}
    mock_get.return_value = mock_response

    condition_codes = "invalid_code"
    clinical_services = await get_clinical_services(condition_codes)
    assert clinical_services[0].status_code == 503
