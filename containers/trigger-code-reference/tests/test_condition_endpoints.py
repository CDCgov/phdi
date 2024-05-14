from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def mock_db():
    with patch("sqlite3.connect", autospec=True) as mock_connect:
        mock_conn = mock_connect.return_value
        mock_conn.__enter__.return_value = mock_conn
        mock_cursor = mock_conn.cursor.return_value
        yield mock_cursor

def test_health_check():
    actual_response = client.get("/")
    assert actual_response.status_code == 200
    assert actual_response.json() == {
        "status": "OK",
    }

def test_get_value_sets_for_condition():
    snowmed_code = "276197005"
    expected_result = [
        ("dxtc", "A36.3|A36", "http://hl7.org/fhir/sid/icd-10-cm"),
        ("sdtc", "772150003", "http://snomed.info/sct"),
    ]
    mock_db.fetchall.return_value = expected_result
    result = get_clinical_services_list(snowmed_code)
    assert result == expected_result

def test_insert_condition_extensions():
    pass
