import pytest

from phdi.harmonization.standardization import _standardize_date
from phdi.harmonization.standardization import _validate_date


def test_standardize_date():
    # Working examples of "real" birth dates
    assert _standardize_date("1977-11-21") == "1977-11-21"
    assert _standardize_date("1980-01-31") == "1980-01-31"

    # Now supply format information
    assert _standardize_date("1977/11/21", "%Y/%m/%d") == "1977-11-21"
    assert _standardize_date("1980/01/31", "%Y/%m/%d") == "1980-01-31"
    assert _standardize_date("01/1980/31", "%m/%Y/%d") == "1980-01-31"
    assert _standardize_date("11-1977-21", "%m-%Y-%d") == "1977-11-21"

    with pytest.raises(ValueError) as e:
        standardize_dob_response = _standardize_date("blah")
        assert "Invalid date supplied: blah" in str(e.value)
        assert standardize_dob_response is None

    # format doesn't match date passed in
    assert _standardize_date("11-1977-21", "%m/%Y/%d") == "1977-11-21"


def test_validate_date():
    # valid dates
    assert _validate_date("1980", "10", "15") is True
    # future dates should be ok in this case
    assert _validate_date("3030", "10", "15") is True
    # future dates should not be ok in this case
    assert _validate_date("3030", "10", "15", True) is False
    # invalid month
    assert _validate_date("2005", "15", "10") is False
    # invalid day
    assert _validate_date("2005", "02", "30") is False
