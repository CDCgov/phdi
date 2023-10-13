import pytest
from datetime import date, datetime

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


def test_invalid_datetime_to_str():
    invalid_string = "10-10-2023"
    with pytest.raises(
        ValueError,
        match=f"Input date {invalid_string} is not in the format 'YYYY-MM-DD'.",
    ):
        datetime_to_str(invalid_string)


def test_unsupported_datetime_to_str():
    unsupported_input = 20231010
    with pytest.raises(
        TypeError,
        match=f"Input date {unsupported_input} is not of type date, datetime, or str.",
    ):
        datetime_to_str(unsupported_input)


def test_invalid_datetime_to_str_with_time():
    invalid_string_with_time = "2023-10-10 15:30"
    with pytest.raises(
        ValueError,
        match=(
            f"Input date {invalid_string_with_time} "
            "is not in the format 'YYYY-MM-DD HH:MM:SS'"
        ),
    ):
        datetime_to_str(invalid_string_with_time, include_time=True)
