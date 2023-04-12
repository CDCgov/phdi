from functools import lru_cache
from pydantic import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    mpi_db_type: Optional[str]
    mpi_dbname: Optional[str]
    mpi_host: Optional[str]
    mpi_user: Optional[str]
    mpi_password: Optional[str]
    mpi_port: Optional[str]
    mpi_patient_table: Optional[str]
    mpi_person_table: Optional[str]


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
