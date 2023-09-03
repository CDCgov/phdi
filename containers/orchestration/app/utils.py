import json
import pathlib
from functools import cache
from pathlib import Path
from frozendict import frozendict


@cache
def load_processing_config(config_name: str) -> dict:
    """
    Load a processing config given its name. Look in the 'custom_configs/' directory
    first. If no custom configs match the provided name, check the configs provided by
    default with this service in the 'default_configs/' directory.

    :param path: The path to an extraction config file.
    :return: A dictionary containing the extraction config.
    """
    custom_config_path = Path(__file__).parent / "custom_configs" / config_name
    try:
        with open(custom_config_path, "r") as file:
            processing_config = json.load(file)
    except FileNotFoundError:
        try:
            default_config_path = (
                Path(__file__).parent / "default_configs" / config_name
            )
            with open(default_config_path, "r") as file:
                processing_config = json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"A config with the name '{config_name}' could not be found."
            )

    return freeze_processing_config(processing_config)


def freeze_processing_config(processing_config: dict) -> frozendict:
    """
    Given a processing config dictionary, freeze it and all of its nested dictionaries
    into a single immutable dictionary.

    :param processing_config: A dictionary containing a processing config.
    :return: A frozen dictionary containing the processing config.
    """
    for field, field_definition in processing_config.items():
        if "secondary_config" in field_definition:
            for secondary_field, secondary_field_definition in field_definition[
                "secondary_config"
            ].items():
                field_definition["secondary_config"][secondary_field] = frozendict(
                    secondary_field_definition
                )
            field_definition["secondary_config"] = frozendict(
                field_definition["secondary_config"]
            )
        processing_config[field] = frozendict(field_definition)
    return frozendict(processing_config)


def read_json_from_assets(filename: str):
    return json.load(open((pathlib.Path(__file__).parent.parent / "assets" / filename)))
