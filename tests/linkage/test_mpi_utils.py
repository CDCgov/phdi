import os

from phdi.linkage.config import get_settings
from phdi.linkage.utils import load_mpi_env_vars_os


def test_get_settings_and_env_vars():
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
