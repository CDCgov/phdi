import json
import pathlib
from app.config import get_settings
from phdi.linkage import DIBBsConnectorClient
import subprocess
from typing import Literal


def connect_to_mpi_with_env_vars():
    """
    Helper function to load MPI Database settings from the relevant
    environment variables, then spin up a connection to the MPI.
    This also automatically tests that a connection can be made as
    part of instantiating the DB Client.
    """
    dbname, user, password, host = load_mpi_env_vars_os()
    port = get_settings().get("mpi_port")
    patient_table = get_settings().get("mpi_patient_table")
    person_table = get_settings().get("mpi_person_table")
    db_client = DIBBsConnectorClient(
        dbname, user, password, host, port, patient_table, person_table
    )
    return db_client


def load_mpi_env_vars_os():
    """
    Simple helper function to load some of the environment variables
    needed to make a database connection as part of the DB migrations.
    """
    dbname = get_settings().get("mpi_dbname")
    user = get_settings().get("mpi_user")
    password = get_settings().get("mpi_password")
    host = get_settings().get("mpi_host")
    return dbname, user, password, host


def read_json_from_assets(filename: str):
    return json.load(open((pathlib.Path(__file__).parent.parent / "assets" / filename)))


def run_pyway(
    pyway_command: Literal["info", "validate", "migrate", "import"]
) -> subprocess.CompletedProcess:
    """
    Helper function to run the pyway CLI from Python.

    :param pyway_command: The specific pyway command to run.
    :return: A subprocess.CompletedProcess object containing the results of the pyway
        command.
    """

    migrations_dir = str(pathlib.Path(__file__).parent.parent / "migrations")
    settings = get_settings()
    pyway_args = [
        f"--database-migration-dir {migrations_dir}",
        f"--database-type {settings['mpi_db_type']}",
        f"--database-host {settings['mpi_host']}",
        f"--database-port {settings['mpi_port']}",
        f"--database-name {settings['mpi_dbname']}",
        f"--database-username {settings['mpi_user']}",
        f"--database-password {settings['mpi_password']}",
    ]
    full_command = ["pyway", pyway_command] + pyway_args
    pyway_response = subprocess.run(
        full_command, shell=True, check=True, capture_output=True
    )

    return pyway_response
