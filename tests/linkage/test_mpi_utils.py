import json
import os
import pathlib

from pydantic import ValidationError
from phdi.linkage.utils import (
    get_address_lines,
    get_geo_latitude,
    get_geo_longitude,
    get_patient_addresses,
    get_patient_ethnicity,
    get_patient_names,
    get_patient_phones,
    get_patient_race,
    load_mpi_env_vars_os,
)
from phdi.linkage.config import DBSettings, get_settings


patient_resource = json.load(
    open(
        pathlib.Path(__file__).parent.parent.parent
        / "tests"
        / "assets"
        / "general"
        / "patient_resource_w_extensions.json"
    )
)


def test_get_settings_and_env_vars():
    try:
        db_settings = get_settings()
        assert 1 == 2
    except ValidationError as error:
        assert error.model == DBSettings

    try:
        db_settings = load_mpi_env_vars_os()
        assert 1 == 2
    except ValidationError as error:
        assert error.model == DBSettings

    os.environ = {
        "mpi_dbname": "testdb",
        "mpi_user": "postgres",
        "mpi_password": "pw",
        "mpi_host": "localhost",
        "mpi_port": "5432",
        "mpi_db_type": "postgres",
    }
    expected_result = {
        "mpi_db_type": "postgres",
        "mpi_dbname": "testdb",
        "mpi_host": "localhost",
        "mpi_user": "postgres",
        "mpi_password": "pw",
        "mpi_port": "5432",
    }
    db_settings = get_settings()
    assert db_settings == expected_result

    db_settings = load_mpi_env_vars_os()
    expected_result = {
        "db_type": "postgres",
        "dbname": "testdb",
        "host": "localhost",
        "user": "postgres",
        "password": "pw",
        "port": "5432",
    }

    assert db_settings == expected_result


def test_get_patient_ethnicity():
    patient_eth = get_patient_ethnicity(patient_resource)

    assert patient_eth == "Hispanic or Latino"
    patient_eth = get_patient_ethnicity({})
    assert patient_eth is None


def test_get_patient_race():
    patient_race = get_patient_race(patient_resource)

    assert patient_race == "White"
    patient_race = get_patient_race({})
    assert patient_race is None


def test_address_lines():
    address = {"address": get_patient_addresses(patient_resource)}
    lines = get_address_lines(address)

    assert len(lines) > 0

    lines = get_address_lines({})
    assert len(lines) == 0


def test_geo_lat():
    address = {"address": get_patient_addresses(patient_resource)}
    lat = get_geo_latitude(address)
    assert lat == 34.58002

    lat = get_geo_latitude({})
    assert lat is None


def test_geo_long():
    address = {"address": get_patient_addresses(patient_resource)}
    lon = get_geo_longitude(address)
    assert lon == -118.08925

    lon = get_geo_longitude({})
    assert lon is None


def test_get_patient_names():
    names = get_patient_names(patient_resource)
    for name in names:
        assert name.get("family") == "doe"
        given_names = name.get("given")
        assert len(given_names) == 2
        assert given_names[0] == "John "
        assert given_names[1] == " Danger "
    names = get_patient_names({})
    assert len(names) == 0


def test_get_patient_phones():
    phones = get_patient_phones(patient_resource)
    for phone in phones:
        assert phone.get("value") == "123-456-7890"
        assert phone.get("system") == "phone"
        assert phone.get("use") == "home"

    phones = get_patient_phones({})
    assert len(phones) == 0
