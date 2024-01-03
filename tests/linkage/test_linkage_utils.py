from datetime import date
from datetime import datetime

import pytest

from phdi.linkage import datetime_to_str


@pytest.mark.parametrize(
    "input_value, expected_output",
    [
        (date(2023, 10, 10), "2023-10-10"),
        (datetime(2023, 10, 10, 15, 30), "2023-10-10"),
        ("2023-10-10", "2023-10-10"),
    ],
)
def test_valid_datetime_to_str(input_value, expected_output):
    assert datetime_to_str(input_value) == expected_output


@pytest.mark.parametrize(
    "input_value, expected_output",
    [
        (date(2023, 10, 10), "2023-10-10 00:00:00"),
        (datetime(2023, 10, 10, 15, 30), "2023-10-10 15:30:00"),
        ("2023-10-10 15:30:00", "2023-10-10 15:30:00"),
    ],
)
def test_valid_datetime_to_str_with_time(input_value, expected_output):
    assert datetime_to_str(input_value, include_time=True) == expected_output


@pytest.mark.parametrize(
    "input_value, expected_output",
    [
        ("", ""),
        (None, None),
        (20231010, "20231010"),
        (["2023-10-10"], "['2023-10-10']"),
        ({"date": "2023-10-10"}, "{'date': '2023-10-10'}"),
    ],
)
def test_bad_input_datetime_to_str(input_value, expected_output):
    assert datetime_to_str(input_value) == expected_output
