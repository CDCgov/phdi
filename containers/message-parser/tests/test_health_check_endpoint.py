from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)

def test_health_check():
    actual_response = client.get("/")
    assert actual_response.status_code == 200
    assert actual_response.json() == {"status": "OK"}