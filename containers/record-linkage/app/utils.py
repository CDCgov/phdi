import json
import logging
import os
import pathlib
import subprocess
from typing import Literal

from sqlalchemy import text

from app.config import get_settings
from app.linkage.dal import DataAccessLayer
from app.linkage.mpi import DIBBsMPIConnectorClient


def read_json_from_assets(filename: str):
    """
    Loads a JSON file from the 'assets' directory.
    """
    return json.load(open((pathlib.Path(__file__).parent.parent / "assets" / filename)))


def run_pyway(
    pyway_command: Literal["info", "validate", "migrate", "import"],
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


def set_mpi_env_vars():
    """
    Utility function for testing purposes that sets the environment variables
    of the testing suite to prespecified valid values, and clears out any
    old values from the DB Settings cache.
    """
    os.environ["mpi_db_type"] = "postgres"
    os.environ["mpi_dbname"] = "testdb"
    os.environ["mpi_user"] = "postgres"
    os.environ["mpi_password"] = "pw"
    os.environ["mpi_host"] = "localhost"
    os.environ["mpi_port"] = "5432"
    get_settings.cache_clear()


def pop_mpi_env_vars():
    """
    Utility function for testing purposes that removes the environment variables
    used for database access from the testing environment.
    """
    os.environ.pop("mpi_db_type", None)
    os.environ.pop("mpi_dbname", None)
    os.environ.pop("mpi_user", None)
    os.environ.pop("mpi_password", None)
    os.environ.pop("mpi_host", None)
    os.environ.pop("mpi_port", None)


def _clean_up(dal: DataAccessLayer | None = None) -> None:
    """
    Utility function for testing purposes that makes tests idempotent by cleaning up
    database state after each test run.

    :param dal: Optionally, a DataAccessLayer currently connected to an instantiated
      MPI database. If not provided, the default DIBBsMPIConnectorClient is used
      to perform cleanup operations.
    """
    if dal is None:
        dal = DIBBsMPIConnectorClient().dal
    with dal.engine.connect() as pg_connection:
        pg_connection.execute(text("""DROP TABLE IF EXISTS external_person CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS external_source CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS address CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS phone_number CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS identifier CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS give_name CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS given_name CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS name CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS patient CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS person CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS public.pyway CASCADE;"""))
        pg_connection.commit()
        pg_connection.close()
