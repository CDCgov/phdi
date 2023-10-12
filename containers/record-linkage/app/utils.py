import json
import logging
import pathlib
import subprocess
from datetime import date, datetime
from typing import Literal, Union

from app.config import get_settings
from phdi.linkage import DIBBsConnectorClient


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
