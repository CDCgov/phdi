import json
import fhirpathpy
from functools import cache


@cache
def load_extraction_schema(path: str) -> dict:
    """
    Given a path load and extraction schema.

    :param path: The path to an extraction schema file.
    :return: A dictionary containing the extraction schema.
    """
    try:
        with open(path, "r") as file:
            extraction_schema = json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(
            "The specified file does not exist at the path provided."
        )
    return extraction_schema


def get_extraction_parsers(extraction_schema: dict) -> dict:
    """
    Generate a FHIRpath parser for each field in a given schema. Return these parsers as
    values in a dictionary whose keys indicate the field in the schema the parser is
    associated with.

    :param extraction_schema: A dictionary containing an extraction schema.
    :return: A dictionary containing a FHIRpath parsers for each field in the provided
    schema.
    """

    parsers = {}

    for field, fhirpath in extraction_schema.items():
        parsers[field] = fhirpathpy.compile(fhirpath)

    return parsers
