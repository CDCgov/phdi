import json
import fhirpathpy
from functools import cache
from pathlib import Path
from frozendict import frozendict


@cache
def load_parsing_schema(schema_name: str) -> dict:
    """
    Given a path load and extraction schema.

    :param path: The path to an extraction schema file.
    :return: A dictionary containing the extraction schema.
    """
    custom_schema_path = Path(__file__).parent / "custom_schemas" / schema_name
    try:
        with open(custom_schema_path, "r") as file:
            extraction_schema = json.load(file)
    except FileNotFoundError:
        try:
            default_schema_path = (
                Path(__file__).parent / "default_schemas" / schema_name
            )
            with open(default_schema_path, "r") as file:
                extraction_schema = json.load(file)
        except:
            raise FileNotFoundError(
                f"A schema with the name '{schema_name}' could not be found."
            )
    return extraction_schema

@cache
def get_parsers(extraction_schema: frozendict) -> frozendict:
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
    return frozendict(parsers)
