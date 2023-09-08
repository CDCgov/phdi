from app.utils import run_pyway
from unittest import mock
import pathlib


@mock.patch("app.utils.get_settings")
@mock.patch("app.utils.subprocess.run")
def test_run_pyway(patched_subprocess, patched_get_settings):
    mock_settings = {
        "mpi_db_type": "postgres",
        "mpi_host": "localhost",
        "mpi_port": "5432",
        "mpi_dbname": "testdb",
        "mpi_user": "postgres",
        "mpi_password": "pw",
    }
    patched_get_settings.return_value = mock_settings
    run_pyway("info")
    migrations_dir = str(pathlib.Path(__file__).parent.parent / "migrations")
    patched_subprocess.assert_called_once_with(
        " ".join([
            "pyway",
            "info",
            f"--database-migration-dir {migrations_dir}",
            "--database-type postgres",
            "--database-host localhost",
            "--database-port 5432",
            "--database-name testdb",
            "--database-username postgres",
            "--database-password pw",
        ]),
        shell=True,
        check=True,
        capture_output=True,
    )
