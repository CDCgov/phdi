from app.main import app
from app.models import RefinerInput
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health_check():
    actual_response = client.get("/")
    assert actual_response.status_code == 200
    assert actual_response.json() == {
        "status": "OK",
    }


def test_refiner(
    input=RefinerInput(
        message="test test",
    ),
    expected_successful_response={"refined_message": "test test"},
):
    actual_response = client.post("/refine-ecr", json=input.dict())
    assert actual_response.status_code == 200
    assert actual_response.json() == expected_successful_response
