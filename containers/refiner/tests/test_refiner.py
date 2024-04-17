from app.main import app
from dibbs.utils import read_file_from_test_assets
from fastapi.testclient import TestClient

client = TestClient(app)

test_xml = read_file_from_test_assets("CDA_eICR.xml")


def test_health_check():
    actual_response = client.get("/")
    assert actual_response.status_code == 200
    assert actual_response.json() == {
        "status": "OK",
    }


def test_ecr_refiner():
    expected_successful_response = {"refined_message": test_xml}
    actual_response = client.post("/ecr", json={"message": test_xml})
    assert actual_response.status_code == 200
    assert actual_response.json() == expected_successful_response
