from functools import lru_cache
from pydantic import BaseSettings


class Settings(BaseSettings):
    fhir_converter_url: str
    validation_url: str
    message_parser_url: str
    ingestion_url: str
    smarty_auth_id: str
    smarty_auth_token: str
    license_type: str


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
