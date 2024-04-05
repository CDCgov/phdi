import pathlib
import subprocess
from typing import Literal
from unittest import mock

import pytest
from app.utils import run_migrations
from app.utils import run_pyway

MOCK_SETTINGS = {
    "mpi_db_type": "postgres",
    "mpi_host": "localhost",
    "mpi_port": "5432",
    "mpi_dbname": "testdb",
    "mpi_user": "postgres",
    "mpi_password": "pw",
}


def make_pyway_command(
    pyway_command: Literal["info", "validate", "migrate", "import"],
) -> str:
    """
    Helper function for tests that require a pyway command.
    :param pyway_command: The specific pyway command to run.
    :return: A string containing the pyway command.
    """

    migrations_dir = str(pathlib.Path(__file__).parent.parent / "migrations")

    pyway_command = " ".join(
        [
            "pyway",
            pyway_command,
            f"--database-migration-dir {migrations_dir}",
            f"--database-type {MOCK_SETTINGS['mpi_db_type']}",
            f"--database-host {MOCK_SETTINGS['mpi_host']}",
            f"--database-port {MOCK_SETTINGS['mpi_port']}",
            f"--database-name {MOCK_SETTINGS['mpi_dbname']}",
            f"--database-username {MOCK_SETTINGS['mpi_user']}",
            f"--database-password {MOCK_SETTINGS['mpi_password']}",
        ]
    )
    return pyway_command


@mock.patch("app.utils.get_settings")
@mock.patch("app.utils.subprocess.run")
def test_run_pyway_success(patched_subprocess, patched_get_settings):
    """
    Test the happy path in run_pyway()
    """
    global MOCK_SETTINGS
    patched_get_settings.return_value = MOCK_SETTINGS
    run_pyway("info")
    pyway_command = make_pyway_command("info")
    patched_subprocess.assert_called_once_with(
        pyway_command,
        shell=True,
        check=True,
        capture_output=True,
    )


@mock.patch("app.utils.get_settings")
@mock.patch("app.utils.subprocess.run")
def test_run_pyway_failure(patched_subprocess, patched_get_settings):
    """
    The general failure mode of run_pyway() when a subprocess.CalledProcessError is
    raised.
    """

    global MOCK_SETTINGS
    patched_get_settings.return_value = MOCK_SETTINGS
    output = mock.Mock()
    output.decode.return_value = "test"
    patched_subprocess.side_effect = subprocess.CalledProcessError(
        returncode=1, cmd="test", stderr="test", output=output
    )
    pyway_command = make_pyway_command("info")
    with pytest.raises(subprocess.CalledProcessError):
        run_pyway("info")
    patched_subprocess.assert_called_once_with(
        pyway_command,
        shell=True,
        check=True,
        capture_output=True,
    )


@mock.patch("app.utils.get_settings")
@mock.patch("app.utils.subprocess.run")
def test_run_pyway_no_migrations(patched_subprocess, patched_get_settings):
    """
    Test the special case where 'pyway validate' returns an error if no migrations have
    been applied yet.
    """

    global MOCK_SETTINGS
    patched_get_settings.return_value = MOCK_SETTINGS
    output = mock.Mock()
    output.decode.return_value = (
        "ERROR: no migrations applied yet, no validation necessary."
    )
    patched_subprocess.side_effect = subprocess.CalledProcessError(
        returncode=1, cmd="test", stderr="test", output=output
    )
    pyway_command = make_pyway_command("validate")
    run_pyway("validate")
    patched_subprocess.assert_called_once_with(
        pyway_command,
        shell=True,
        check=True,
        capture_output=True,
    )


@mock.patch("app.utils.run_pyway")
def test_run_migrations_success(patched_run_pyway):
    """
    Test the happy path in run_migrations()
    """
    validation_response = mock.Mock()
    validation_response.returncode = 0
    migration_response = mock.Mock()
    migration_response.returncode = 0
    patched_run_pyway.side_effect = [validation_response, migration_response]
    run_migrations()
    patched_run_pyway.assert_has_calls([mock.call("validate"), mock.call("migrate")])


@mock.patch("app.utils.run_pyway")
def test_run_migrations_validation_failure(patched_run_pyway):
    """
    Test the case where the validation step fails in run_migrations().
    """
    validation_response = mock.Mock()
    validation_response.returncode = 1
    migration_response = mock.Mock()
    migration_response.returncode = 0
    patched_run_pyway.side_effect = [validation_response, migration_response]
    with pytest.raises(Exception):
        run_migrations()
    patched_run_pyway.assert_called_once_with("validate")


@mock.patch("app.utils.run_pyway")
def test_run_migrations_migration_failure(patched_run_pyway):
    """
    Test the case where the migration step fails in run_migrations().
    """
    validation_response = mock.Mock()
    validation_response.returncode = 0
    migration_response = mock.Mock()
    migration_response.returncode = 1
    patched_run_pyway.side_effect = [validation_response, migration_response]
    with pytest.raises(Exception):
        run_migrations()
    patched_run_pyway.assert_has_calls([mock.call("validate"), mock.call("migrate")])
