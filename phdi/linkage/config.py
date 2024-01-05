from functools import lru_cache

from pydantic import BaseSettings


class DBSettings(BaseSettings):
    mpi_db_type: str
    mpi_dbname: str
    mpi_host: str
    mpi_user: str
    mpi_password: str
    mpi_port: str


@lru_cache()
def get_settings() -> dict:
    """
    Load the values specified in the Settings class from the environment and return a
    dictionary containing them. The dictionary is cached to reduce overhead accessing
    these values.

    :return: A dictionary with keys specified by the Settings. The value of each key is
    read from the corresponding environment variable.
    """
    return DBSettings().dict()
