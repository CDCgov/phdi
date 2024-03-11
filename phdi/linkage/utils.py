from datetime import date
from datetime import datetime
from typing import Union

from phdi.linkage.config import get_settings


def load_mpi_env_vars_os():
    """
    Simple helper function to load some of the environment variables
    needed to make a database connection as part of the DB migrations.
    """
    dbsettings = {
        "dbname": get_settings().get("mpi_dbname"),
        "user": get_settings().get("mpi_user"),
        "password": get_settings().get("mpi_password"),
        "host": get_settings().get("mpi_host"),
        "port": get_settings().get("mpi_port"),
        "db_type": get_settings().get("mpi_db_type"),
    }
    return dbsettings


# TODO:  Not sure if we will need this or not
# leaving in utils for now until it's determined that
# we won't need to use this within any of the DAL/MPI/LINK
# code
# # https://kb.objectrocket.com/postgresql
# /python-error-handling-with-the-psycopg2-postgresql-adapter-645
# def print_psycopg2_exception(err):
#     # get details about the exception
#     err_type, _, traceback = sys.exc_info()

#     # get the line number when exception occured
#     line_num = traceback.tb_lineno

#     # print the connect() error
#     print("\npsycopg2 ERROR:", err, "on line number:", line_num)
#     print("psycopg2 traceback:", traceback, "-- type:", err_type)

#     # psycopg2 extensions.Diagnostics object attribute
#     print("\nextensions.Diagnostics:", err.diag)

#     # print the pgcode and pgerror exceptions
#     print("pgerror:", err.pgerror)
#     print("pgcode:", err.pgcode, "\n")


def datetime_to_str(
    input_date: Union[str, date, datetime], include_time: bool = False
) -> str:
    """
    Convert a date or datetime object to a string; if a string is provided,
    check that it follows the appropriate format. If unable to perform actions,
    return input as string rather than failing loudly.

    :param input_date: The input date to convert, which prefers types of
        datetime.date, datetime.datetime, or str.
    :param include_time: Whether to include the time in the output string.
    :return: The formatted date as a string. If include_time is True, the
        format is 'YYYY-MM-DD HH:MM:SS', otherwise it's 'YYYY-MM-DD'. If
        empty or None, return empty or None.
    """
    # Handle None or empty string
    if input_date is None or input_date == "":
        return input_date

    # if input is str try to check that it follows the expected format
    if isinstance(input_date, str):
        try:
            expected_format = "%Y-%m-%d %H:%M:%S" if include_time else "%Y-%m-%d"
            datetime.strptime(input_date, expected_format)
            return input_date
        except ValueError:
            # rather than break loudly, allow str to pass
            return input_date

    # if input is a date or datetime then convert in the expected format
    elif isinstance(input_date, (date, datetime)):
        if include_time:
            return input_date.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return input_date.strftime("%Y-%m-%d")
    # if input isn't any of the accepted formats, then return a type error
    else:
        try:
            return str(input_date)
        except TypeError:
            raise TypeError(
                f"Input date {input_date} is not of type date, datetime, "
                "or str; or, it can't be converted or returned safely."
            )
