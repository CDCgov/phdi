import sqlite3
from unittest.mock import patch

import pytest
from app.utils import get_clean_snomed_code
from app.utils import get_clinical_services_dict
from app.utils import get_clinical_services_list
from app.utils import sanitize_inputs_to_list


@pytest.fixture
def mock_db():
    with patch("sqlite3.connect", autospec=True) as mock_connect:
        mock_conn = mock_connect.return_value
        mock_conn.__enter__.return_value = mock_conn
        mock_cursor = mock_conn.cursor.return_value
        yield mock_cursor


# tests to confirm sanitize inputs work
def test_sanitize_inputs_to_list_single_value():
    assert sanitize_inputs_to_list("12345") == ["12345"]


def test_sanitize_inputs_to_list_multiple_values():
    assert sanitize_inputs_to_list("12345,67890") == ["12345", "67890"]


# tests to confirm snomed checks work
def test_get_clean_snomed_code_single():
    assert get_clean_snomed_code("12345") == ["12345"]


def test_get_clean_snomed_code_multiple():
    result = get_clean_snomed_code("12345,67890")
    assert "error" in result
    assert "2 SNOMED codes provided" in result["error"]


# Test getting clinical code list of tuples with a valid SNOMED ID
def test_get_clinical_services_list_normal(mock_db):
    code = 276197005
    expected_result = [
        ("dxtc", "A36.3|A36", "http://hl7.org/fhir/sid/icd-10-cm"),
        ("sdtc", "772150003", "http://snomed.info/sct"),
    ]
    mock_db.fetchall.return_value = expected_result
    result = get_clinical_services_list([code])
    assert result == expected_result


# Test with bad SNOMED code
def test_get_clinical_services_list_no_results(mock_db):
    code = ["junk_id"]
    mock_db.fetchall.return_value = []
    result = get_clinical_services_list(code)
    assert result == {"error": f"No data found for the SNOMED code: {code}."}


# Test SQL error messaging
def test_get_clinical_services_list_sql_error(mock_db):
    snomed_id = 276197005
    mock_db.execute.side_effect = sqlite3.Error("SQL error")
    result = get_clinical_services_list([snomed_id])
    assert "error" in result
    assert "SQL error" in result["error"]


# Test transforming clinical services list to nested dictionary
def test_get_clinical_services_dict_normal():
    clinical_services_list = [
        ("dxtc", "A36.3|A36", "http://hl7.org/fhir/sid/icd-10-cm"),
        ("sdtc", "772150003", "http://snomed.info/sct"),
    ]
    expected_result = {
        "dxtc": [
            {"codes": ["A36.3", "A36"], "system": "http://hl7.org/fhir/sid/icd-10-cm"}
        ],
        "sdtc": [{"codes": ["772150003"], "system": "http://snomed.info/sct"}],
    }
    result = get_clinical_services_dict(clinical_services_list)
    assert result == expected_result


# Test clinical services dict limiting to just sdtc
def test_get_clinical_services_dict_filter_services():
    clinical_services_list = [
        ("dxtc", "A36.3|A36", "http://hl7.org/fhir/sid/icd-10-cm"),
        ("sdtc", "772150003", "http://snomed.info/sct"),
    ]
    filtered_services = ["sdtc"]
    expected_result = {
        "sdtc": [{"codes": ["772150003"], "system": "http://snomed.info/sct"}],
    }
    result = get_clinical_services_dict(clinical_services_list, filtered_services)
    assert result == expected_result
