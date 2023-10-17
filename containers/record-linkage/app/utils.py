import json
import pathlib
from app.config import get_settings
import subprocess
from typing import Literal
import logging
from phdi.linkage.mpi import PGMPIConnectorClient


def connect_to_mpi_with_env_vars():
    """
    Helper function to load MPI Database settings from the relevant
    environment variables, then spin up a connection to the MPI.
    This also automatically tests that a connection can be made as
    part of instantiating the DB Client.
    """
    db_client = PGMPIConnectorClient()
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

    logger = logging.getLogger(__name__)

    # Prepare the pyway command.
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
    full_command = " ".join(full_command)

    # Attempt to run the pyway command.
    try:
        pyway_response = subprocess.run(
            full_command, shell=True, check=True, capture_output=True
        )
    except subprocess.CalledProcessError as error:
        error_message = error.output.decode("utf-8")

        # Pyway validate returns an error if no migrations have been applied yet.
        # This is expected behavior, so we can ignore this error and continue onto
        # the migrations with pyway migrate. We'll encounter this error when we
        # first deploy the service with a fresh database.
        if (
            "ERROR: no migrations applied yet, no validation necessary."
            in error_message
        ):
            logger.warning(error_message)
            return subprocess.CompletedProcess(
                args=full_command,
                returncode=0,
                stdout=None,
                stderr=error_message,
            )
        else:
            logger.error(error_message)
            raise error

    logger.info(pyway_response.stdout.decode("utf-8"))

    return pyway_response


def run_migrations():
    """
    Use the pyway CLI to ensure that the MPI database is up to date with the latest
    migrations.
    """
    logger = logging.getLogger(__name__)
    logger.info("Validating MPI database schema...")
    validation_response = run_pyway("validate")

    if validation_response.returncode == 0:
        logger.info("MPI database schema validations successful.")

        logger.info("Migrating MPI database...")
        migrations_response = run_pyway("migrate")

        if migrations_response.returncode == 0:
            logger.info("MPI database migrations successful.")
        else:
            logger.error("MPI database migrations failed.")
            raise Exception(migrations_response.stderr.decode("utf-8"))

    else:
        logger.error("MPI database schema validations failed.")
        raise Exception(validation_response.stderr.decode("utf-8"))
