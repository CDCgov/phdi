import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.utils import (
    read_json_from_assets,
    standardize_name,
    _standardize_date,
    _validate_date,
)

client = TestClient(app)


@pytest.fixture
def single_patient_bundle():
    return read_json_from_assets("single_patient_bundle.json")


def test_health_check():
    actual_response = client.get("/")
    assert actual_response.status_code == 200
    assert actual_response.json() == {
        "status": "OK",
    }


def test_standardize_name():
    # Basic case of input string
    raw_text = " 12 dIBbs is ReaLLy KEWL !@#$ 34"
    assert (
        standardize_name(raw_text, trim=True, case="lower", remove_numbers=False)
        == "12 dibbs is really kewl  34"
    )
    assert (
        standardize_name(raw_text, trim=True, remove_numbers=True, case="title")
        == "Dibbs Is Really Kewl"
    )
    assert (
        standardize_name(raw_text, trim=False, remove_numbers=True, case="title")
        == "  Dibbs Is Really Kewl  "
    )
    # Now check that it handles list inputs
    names = ["Johnny T. Walker", " Paul bunYAN", "J;R;R;tOlK.iE87n 999"]
    assert standardize_name(names, trim=True, remove_numbers=False) == [
        "JOHNNY T WALKER",
        "PAUL BUNYAN",
        "JRRTOLKIE87N 999",
    ]


@pytest.mark.parametrize(
    "input_date, format_string, future, expected",
    [
        ("1977-11-21", None, False, "1977-11-21"),
        ("1980-01-31", None, False, "1980-01-31"),
        ("1977/11/21", "%Y/%m/%d", False, "1977-11-21"),
        ("1980/01/31", "%Y/%m/%d", False, "1980-01-31"),
        ("01/1980/31", "%m/%Y/%d", False, "1980-01-31"),
        ("11-1977-21", "%m-%Y-%d", False, "1977-11-21"),
    ],
)
def test_standardize_date(input_date, format_string, future, expected):
    if format_string:
        assert _standardize_date(input_date, format_string, future) == expected
    else:
        assert _standardize_date(input_date, future=future) == expected


def test_standardize_date_invalid():
    with pytest.raises(ValueError) as e:
        _standardize_date("blah")
    assert "Invalid date format or missing components in date: blah" in str(e.value)


def test_standardize_date_format_mismatch():
    with pytest.raises(ValueError) as e:
        _standardize_date("abc-def-ghi", "%Y-%m-%d")
    assert "Invalid date format supplied:" in str(e.value)

    with pytest.raises(ValueError) as e:
        _standardize_date("1980-01-31", "%H:%M:%S")
    assert "Invalid date format or missing components in date:" in str(e.value)


@pytest.mark.parametrize(
    "year, month, day, allow_future, expected",
    [
        ("1980", "10", "15", False, True),
        ("3030", "10", "15", False, True),
        ("3030", "10", "15", True, False),
        ("2005", "15", "10", False, False),
        ("2005", "02", "30", False, False),
    ],
)
def test_validate_date(year, month, day, allow_future, expected):
    assert _validate_date(year, month, day, allow_future) == expected
