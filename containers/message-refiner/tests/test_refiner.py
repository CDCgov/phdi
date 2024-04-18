import pytest
from app.main import app
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
