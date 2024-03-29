import json
import logging
import pathlib
import random
import subprocess
from functools import cache
from importlib import metadata
from pathlib import Path
from typing import Any
from typing import Callable
from typing import List
from typing import Literal
from typing import Union

import fhirpathpy
from app.config import get_settings
from fastapi import FastAPI
from pydantic import BaseModel


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


# Originally from phdi/fhir/utils.py
# TODO: Move this to the dibbs SDK once created
# create a class with the DIBBs default Creative Commons Zero v1.0 and
# MIT license to be used by the BaseService class
LICENSES = {
    "CreativeCommonsZero": {
        "name": "Creative Commons Zero v1.0 Universal",
        "url": "https://creativecommons.org/publicdomain/zero/1.0/",
    },
    "MIT": {"name": "The MIT License", "url": "https://mit-license.org/"},
}

DIBBS_CONTACT = {
    "name": "CDC Public Health Data Infrastructure",
    "url": "https://cdcgov.github.io/phdi-site/",
    "email": "dmibuildingblocks@cdc.gov",
}


STATUS_OK = {"status": "OK"}


# Originally from phdi/fhir/utils.py
# TODO: Move this to the dibbs SDK once created
class StatusResponse(BaseModel):
    """
    The schema for the response from the health check endpoint.
    """

    status: Literal["OK"]


selection_criteria_types = Literal["first", "last", "random", "all"]


# Originally from phdi/fhir/utils.py
# TODO: Move this to the dibbs SDK once created
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
    if type(value) is dict:  # pragma: no cover
        value = json.dumps(value)
    elif type(value) is list:
        value = ",".join(value)
    return value


# Originally from phdi/fhir/utils.py
# TODO: Move this to the dibbs SDK once created
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


# Originally from phdi/fhir/utils.py
# TODO: Move this to the dibbs SDK once created
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


# Originally from phdi/containers/base_service.py
# TODO: Move this to the dibbs SDK once created
class BaseService:
    def __init__(
        self,
        service_name: str,
        service_path: str,
        description_path: str,
        include_health_check_endpoint: bool = True,
        license_info: Literal["CreativeCommonsZero", "MIT"] = "CreativeCommonsZero",
    ):
        """
        Initialize a BaseService instance.

        :param service_name: The name of the service.
        :param service_path: The path to used to access the service from a gateway.
        :param description_path: The path to a markdown file containing a description of
            the service.
        :param include_health_check_endpoint: If True, the standard DIBBs health check
            endpoint will be added.
        :param license_info: If empty, the standard DIBBs Creative Commons Zero v1.0
            Universal license will be used. The other available option is to use the
            MIT license.
        """
        description = Path(description_path).read_text(encoding="utf-8")
        self.service_path = service_path
        self.include_health_check_endpoint = include_health_check_endpoint
        self.app = FastAPI(
            title=service_name,
            version=metadata.version("phdi"),
            contact=DIBBS_CONTACT,
            license_info=LICENSES[license_info],
            description=description,
        )

    def add_path_rewrite_middleware(self):
        """
        Add middleware to the FastAPI instance to strip the service_path
        from the URL path if it is present. This is useful when the service
        is behind a gateway that is using a path-based routing strategy.
        """

        @self.app.middleware("http")
        async def rewrite_path(request, call_next):
            if request.url.path.startswith(self.service_path):
                request.scope["path"] = request.scope["path"].replace(
                    self.service_path, ""
                )
                if request.scope["path"] == "":
                    request.scope["path"] = "/"
            return await call_next(request)

    def add_health_check_endpoint(self):
        @self.app.get("/")
        async def health_check() -> StatusResponse:
            """
            Check service status. If an HTTP 200 status code is returned along with
            '{"status": "OK"}' then the service is available and running properly.
            """
            return STATUS_OK

    def start(self) -> FastAPI:
        """
        Return a FastAPI instance with DIBBs metadata set. If
        `include_health_check_endpoint` is True, then the health check endpoint
        will be added.

        :return: The FastAPI instance.
        """
        self.add_path_rewrite_middleware()
        if self.include_health_check_endpoint:
            self.add_health_check_endpoint()
        return self.app
