import sqlite3
from unittest.mock import patch

import pytest
from app.utils import get_clinical_service_dict


@pytest.fixture
def mock_db():
    with patch("sqlite3.connect", autospec=True) as mock_connect:
        mock_conn = mock_connect.return_value
        mock_conn.__enter__.return_value = mock_conn
        mock_cursor = mock_conn.cursor.return_value
        yield mock_cursor


# Test normal behavior with a valid SNOMED ID
def test_get_clinical_service_dict_normal(mock_db):
    snomed_id = 276197005
    expected_result = {
        "dxtc": [
            {"codes": ["A36.3", "A36"], "system": "http://hl7.org/fhir/sid/icd-10-cm"}
        ],
        "sdtc": [{"codes": ["772150003"], "system": "http://snomed.info/sct"}],
    }
    mock_db.fetchall.return_value = [
        ("dxtc", "A36.3|A36", "http://hl7.org/fhir/sid/icd-10-cm"),
        ("sdtc", "772150003", "http://snomed.info/sct"),
    ]
    result = get_clinical_service_dict(snomed_id)
    assert result == expected_result


# Test normal behavior with a valid SNOMED ID, trimming to just sdtc
def test_get_clinical_service_dict_with_clinical_service_paramater(mock_db):
    snomed_id = 276197005
    expected_result = {
        "sdtc": [{"codes": ["772150003"], "system": "http://snomed.info/sct"}]
    }
    mock_db.fetchall.return_value = [
        ("dxtc", "A36.3|A36", "http://hl7.org/fhir/sid/icd-10-cm"),
        ("sdtc", "772150003", "http://snomed.info/sct"),
    ]
    result = get_clinical_service_dict(snomed_id, "sdtc")
    assert result == expected_result


# Test handling no results found for an invalid SNOMED ID
def test_get_clinical_service_dict_no_results(mock_db):
    snomed_id = "junk_id"
    mock_db.fetchall.return_value = []
    result = get_clinical_service_dict(snomed_id)
    assert result == {"error": "No data found for the SNOMED code: junk_id."}


# Test SQL error handling
def test_get_clinical_service_dict_sql_error(mock_db):
    snomed_id = 276197005
    mock_db.execute.side_effect = sqlite3.Error("SQL error")
    result = get_clinical_service_dict(snomed_id)
    assert "error" in result
    assert "SQL error" in result["error"]


# Test invalid input (multiple IDs)
def test_get_clinical_service_dict_invalid_input():
    snomed_id = "276197005, 789012"
    result = get_clinical_service_dict(snomed_id)
    assert result == {
        "error": "2 SNOMED codes provided. " + "Provide only one SNOMED code."
    }
