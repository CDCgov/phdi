from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_health_check():
    actual_response = client.get("/")
    assert actual_response.status_code == 200
    assert actual_response.json() == {"status": "OK"}


def test_validate_valid_ecr():
    request_body = {"message_type": "ecr", "message": "my ecr"}
    actual_response = client.post("/validate", json=request_body)
    assert actual_response.status_code == 200
    assert actual_response.json() == {
        "message_valid": True,
        "validation_results": {
            "details": "No validation was actually preformed. This endpoint only has "
            "stubbed functionality"
        },
    }
