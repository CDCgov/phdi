import fhirpathpy
import json
import random
from functools import cache
from typing import Any, Callable, List, Literal, Union
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


@cache
def _get_fhirpathpy_parser(fhirpath_expression: str) -> Callable:
    """
    Accepts a FHIRPath expression, and returns a callable function
    which returns the evaluated value at fhirpath_expression for
    a specified FHIR resource.
    :param fhirpath_expression: The FHIRPath expression to evaluate.
    :return: A function that, when called passing in a FHIR resource,
      will return value at `fhirpath_expression`.
    """
    return fhirpathpy.compile(fhirpath_expression)


def get_patient_race(patient_resource: dict) -> str:
    parse_function = _get_fhirpathpy_parser(
        "where(resourceType = 'Patient').extension.where(url = "
        + "'http://hl7.org/fhir/us/core/StructureDefinition/"
        + "us-core-race').extension.valueCoding.display"
    )
    patient_race = parse_function(patient_resource)
    return patient_race[0]


def get_patient_ethnicity(patient_resource: dict) -> str:
    parse_function = _get_fhirpathpy_parser(
        "where(resourceType = 'Patient').extension.where(url = "
        + "'http://hl7.org/fhir/us/core/StructureDefinition/"
        + "us-core-ethnicity').extension.valueCoding.display"
    )
    patient_ethnicity = parse_function(patient_resource)
    return patient_ethnicity[0]


def get_patient_identifiers(patient_resource: dict) -> list:
    parse_function = _get_fhirpathpy_parser(
        "where(resourceType = 'Patient').identifier"
    )
    indentifiers = parse_function(patient_resource)
    return indentifiers


def get_patient_phones(patient_resource: dict) -> list:
    parse_function = _get_fhirpathpy_parser(
        "where(resourceType = 'Patient').telecom.where(system='phone')"
    )
    phones = parse_function(patient_resource)
    return phones


def get_patient_names(patient_resource: dict) -> list:
    parse_function = _get_fhirpathpy_parser("where(resourceType = 'Patient').name")
    names = parse_function(patient_resource)
    return names


def get_patient_addresses(patient_resource: dict) -> list:
    parse_function = _get_fhirpathpy_parser("where(resourceType = 'Patient').address")
    addresses = parse_function(patient_resource)
    return addresses


def get_address_lines(address_resource: dict) -> list:
    parse_function = _get_fhirpathpy_parser("address.line")
    lines = parse_function(address_resource)
    return lines


def get_geo_latitude(address_resource: dict) -> float:
    parse_function = _get_fhirpathpy_parser(
        "address.extension.where(url='http://hl7.org/"
        + "fhir/StructureDefinition/geolocation')."
        + "extension.where(url='latitude').valueDecimal"
    )
    geo_lat = parse_function(address_resource)
    return geo_lat[0]


def get_geo_longitude(address_resource: dict) -> float:
    parse_function = _get_fhirpathpy_parser(
        "address.extension.where(url='http://hl7.org/"
        + "fhir/StructureDefinition/geolocation')."
        + "extension.where(url='longitude').valueDecimal"
    )
    geo_lat = parse_function(address_resource)
    return geo_lat[0]


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
