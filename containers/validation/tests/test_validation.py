from fastapi.testclient import TestClient
from unittest import mock
from app.main import app


client = TestClient(app)


def test_health_check():
    actual_response = client.get("/")
    assert actual_response.status_code == 200
    assert actual_response.json() == {"status": "OK"}

@mock.patch("app.main.validate_ecr")
def test_validate_endpoint_valid_ecr():
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

def test_validate_endpoint_valid_elr():
    request_body = {"message_type": "elr", "message": "my ELR"}
    actual_response = client.post("/validate", json=request_body)
    assert actual_response.status_code == 200
    assert actual_response.json() == {
        "message_valid": True,
        "validation_results": {
            "details": "No validation was actually preformed. This endpoint only has "
            "stubbed functionality"
        },
    }
@mock.patch("app.main.validate_ecr")
def test_validate_endpoint_valid_vxu():
    request_body = {"message_type": "vxu", "message": "my VXU"}
    actual_response = client.post("/validate", json=request_body)
    assert actual_response.status_code == 200
    assert actual_response.json() == {
        "message_valid": True,
        "validation_results": {
            "details": "No validation was actually preformed. This endpoint only has "
            "stubbed functionality"
        },
    }