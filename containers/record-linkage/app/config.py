from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    mpi_db_type: str = Field(
        description="The type of database used by the MPI",
    )
    mpi_dbname: str = Field(
        description="The name of the database used by the MPI",
    )
    mpi_host: str = Field(
        description="The host name of the MPI database",
    )
    mpi_user: str = Field(
        description="The name of the user used to connect to the MPI database",
    )
    mpi_password: str = Field(
        description="The password used to connect to the MPI database",
    )
    mpi_port: str = Field(description="The port used to connect to the MPI database")
    connection_pool_size: Optional[int] = Field(
        description="The number of MPI database connections in the connection pool",
        default=5,
    )
    connection_pool_max_overflow: Optional[int] = Field(
        description="The maximum number of MPI database connections that can be opened "
        "above the connection pool size",
        default=10,
    )


@lru_cache()
def get_settings() -> dict:
    """
    Load the values specified in the Settings class from the environment and return a
    dictionary containing them. The dictionary is cached to reduce overhead accessing
    these values.

    :return: A dictionary with keys specified by the Settings. The value of each key is
    read from the corresponding environment variable.
    """
    return Settings().dict()
