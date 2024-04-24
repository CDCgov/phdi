import pytest
from app.main import app
from app.main import validate_sections_to_include
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health_check():
    actual_response = client.get("/")
    assert actual_response.status_code == 200
    assert actual_response.json() == {
        "status": "OK",
    }


test_xml = '<?xml version="1.0" encoding="UTF-8"?>'


@pytest.mark.parametrize(
    "test_data, expected_result",
    [
        # Test case: sections_to_include = None
        (
            {
                "test_xml": test_xml,
                "sections_to_include": None,
            },
            test_xml,
        ),
        # Test case: sections_to_include = "section_1,section2"
        (
            {
                "test_xml": test_xml,
                "sections_to_include": "section_1,section2",
            },
            test_xml,
        ),
    ],
)
def test_ecr_refiner(test_data, expected_result):
    sections_to_include = test_data["sections_to_include"]
    content = test_data["test_xml"]
    endpoint = "/ecr/"
    if sections_to_include:
        endpoint = f"/ecr/?{sections_to_include}"

    actual_response = client.post(endpoint, content=content)

    assert actual_response.status_code == 200
    assert actual_response.content.decode() == expected_result


@pytest.mark.parametrize(
    "test_data, expected_result",
    [
        # Test case: single sections_to_include
        (
            "history of present illness",
            ["10164-2"],
        ),
        # Test case: multiple sections_to_include
        (
            "history of present illness,reason for visit",
            ["10164-2", "29299-5"],
        ),
        # Test case: no sections_to_include
        (
            None,
            None,
        ),
        # Test case: invalid sections_to_include
        (
            "blah blah blah",
            ValueError("blah blah blah is invalid. Please provide a valid section."),
        ),
    ],
)
def test_validate_sections_to_include(test_data, expected_result):
    if isinstance(expected_result, ValueError):
        with pytest.raises(ValueError) as e:
            validate_sections_to_include(test_data)
            assert str(e.value) == str(expected_result)
    elif test_data is None:
        actual_response = validate_sections_to_include(test_data)
        assert actual_response == expected_result
        assert actual_response is None
    else:
        actual_response = validate_sections_to_include(test_data)
        assert actual_response == expected_result
        assert isinstance(actual_response, list)
