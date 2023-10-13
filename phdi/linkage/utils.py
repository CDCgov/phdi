from datetime import date, datetime
from typing import Union

def datetime_to_str(
    input_date: Union[str, date, datetime], include_time: bool = False
) -> str:
    """
    Convert a date or datetime object to a string; if a string is provided,
    check that it follows the appropriate format.

    :param input_date: The input date to convert, which can be of type
        datetime.date, datetime.datetime, or str.
    :param include_time: Whether to include the time in the output string.
    :return: The formatted date as a string. If include_time is True, the
        format is 'YYYY-MM-DD HH:MM:SS', otherwise it's 'YYYY-MM-DD'.
    """
    # if input is str make sure it follows the expected format
    if isinstance(input_date, str):
        try:
            expected_format = "%Y-%m-%d %H:%M:%S" if include_time else "%Y-%m-%d"
            datetime.strptime(input_date, expected_format)
            return input_date
        except ValueError:
            format_msg = " 'YYYY-MM-DD HH:MM:SS' " if include_time else " 'YYYY-MM-DD' "
            raise ValueError(
                f"Input date {input_date} is not in the format" + format_msg
            )
    # if input is a date or datetime then convert in the expected format
    elif isinstance(input_date, (date, datetime)):
        if include_time:
            return input_date.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return input_date.strftime("%Y-%m-%d")
    # if input isn't any of the accepted formats, then return a type error
    else:
        raise TypeError(
            f"Input date {input_date} is not of type date, datetime, or str."
        )
