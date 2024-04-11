import json
import random
from datetime import date
from datetime import datetime
from functools import cache
from typing import Any
from typing import Callable
from typing import List
from typing import Literal
from typing import Union

import fhirpathpy
import rapidfuzz

from app.config import get_settings


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


# Originally from phdi/harmonization/utils.py
def compare_strings(
    string1: str,
    string2: str,
    similarity_measure: Literal[
        "JaroWinkler", "Levenshtein", "DamerauLevenshtein"
    ] = "JaroWinkler",
) -> float:
    """
    Returns the normalized similarity measure between string1 and string2, as
    determined by the similarlity measure. The higher the normalized similarity measure
    (up to 1.0), the more similar string1 and string2 are. A normalized similarity
    measure of 0.0 means string1 and string 2 are not at all similar. This function
    expects basic text cleaning (e.g. removal of numeric characters, trimming of spaces,
    etc.) to already have been performed on the input strings.

    :param string1: First string for comparison.
    :param string2: Second string for comparison.
    :param similarity_measure: The method used to measure the similarity between two
        strings, defaults to "JaroWinkler".
     - JaroWinkler: a ratio of matching characters and transpositions needed to
        transform string1 into string2.
     - Levenshtein: the number of edits (excluding transpositions) needed to transform
        string1 into string2.
     - DamerauLevenshtein: the number of edits (including transpositions) needed to
        transform string1 into string2.
    :return: The normalized similarity between string1 and string2, with 0 representing
        no similarity between string1 and string2, and 1 meaning string1 and string2 are
        dentical words.
    """
    if similarity_measure == "JaroWinkler":
        return rapidfuzz.distance.JaroWinkler.normalized_similarity(string1, string2)
    elif similarity_measure == "Levenshtein":
        return rapidfuzz.distance.Levenshtein.normalized_similarity(string1, string2)
    elif similarity_measure == "DamerauLevenshtein":
        return rapidfuzz.distance.DamerauLevenshtein.normalized_similarity(
            string1, string2
        )


selection_criteria_types = Literal["first", "last", "random", "all"]


def apply_selection_criteria(
    value: List[Any],
    selection_criteria: selection_criteria_types,
) -> str | List:
    """
    Returns value(s), according to the selection criteria, from a given list of values
    parsed from a FHIR resource. A single string value is returned - if the selected
    value is a complex structure (list or dict), it is converted to a string.
    :param value: A list containing the values parsed from a FHIR resource.
    :param selection_criteria: A string indicating which element(s) of a list to select.
    :return: Value(s) parsed from a FHIR resource that conform to the selection
      criteria.
    """

    if selection_criteria == "first":
        value = value[0]
    elif selection_criteria == "last":
        value = value[-1]
    elif selection_criteria == "random":
        value = random.choice(value)
    elif selection_criteria == "all":
        return value
    else:
        raise ValueError(
            f'Selection criteria {selection_criteria} is not a valid option. Must be one of "first", "last", "random", or "all".'  # noqa
        )

    # Temporary hack to ensure no structured data is written using pyarrow.
    # Currently Pyarrow does not support mixing non-structured and structured data.
    # https://github.com/awslabs/aws-data-wrangler/issues/463
    # Will need to consider other methods of writing to parquet if this is an essential
    # feature.
    if isinstance(type(value), dict):  # pragma: no cover
        value = json.dumps(value)
    elif isinstance(type(value), list):
        value = ",".join(value)
    return value


def extract_value_with_resource_path(
    resource: dict,
    path: str,
    selection_criteria: Literal["first", "last", "random", "all"] = "first",
) -> Union[Any, None]:
    """
    Yields a single value from a resource based on a provided `fhir_path`.
    If the path doesn't map to an extant value in the first, returns
    `None` instead.
    :param resource: The FHIR resource to extract a value from.
    :param path: The `fhir_path` at which the value can be found in the
      resource.
    :param selection_criteria: A string dictating which value to extract,
      if multiple values exist at the path location.
    :return: The extracted value, or `None` if the value doesn't exist.
    """
    parse_function = get_fhirpathpy_parser(path)
    value = parse_function(resource)
    if len(value) == 0:
        return None
    else:
        value = apply_selection_criteria(value, selection_criteria)
        return value


@cache
def get_fhirpathpy_parser(fhirpath_expression: str) -> Callable:
    """
    Accepts a FHIRPath expression, and returns a callable function
    which returns the evaluated value at fhirpath_expression for
    a specified FHIR resource.
    :param fhirpath_expression: The FHIRPath expression to evaluate.
    :return: A function that, when called passing in a FHIR resource,
      will return value at `fhirpath_expression`.
    """
    return fhirpathpy.compile(fhirpath_expression)
