from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    Settings confirms the URLs for each of the services being called;
      These urls need to live in a .env file at the root (orchestration) level
      and should be set
    """

    fhir_converter_url: str
    validation_url: str
    message_parser_url: str
    ingestion_url: str
    trigger_code_reference_url: str


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
