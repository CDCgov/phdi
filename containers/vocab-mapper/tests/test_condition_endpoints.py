from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health_check():
    actual_response = client.get("/")
    assert actual_response.status_code == 200
    assert actual_response.json() == {
        "status": "OK",
    }


def test_get_value_sets_for_condition():
    pass


def test_insert_condition_extensions():
    pass
