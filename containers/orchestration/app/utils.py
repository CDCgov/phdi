import re
import json
import pathlib
from functools import cache
from pathlib import Path
from typing import Dict
from zipfile import ZipFile


@cache
def load_processing_config(config_name: str) -> dict:
    """
    Load a processing config given its name. Look in the 'custom_configs/' directory
    first. If no custom configs match the provided name, check the configs provided by
    default with this service in the 'default_configs/' directory.

    :param config_name: Name of config file
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

    return processing_config


def read_json_from_assets(filename: str):
    return json.load(open((pathlib.Path(__file__).parent.parent / "assets" / filename)))


def unzip_ws(zipped_file) -> Dict:
    my_zipfile = zipped_file
    if my_zipfile.namelist:
        try:
            file_to_open = [
                file for file in my_zipfile.namelist() if re.search("CDA_eICR.xml", file, re.I) in file
            ][0]
        except IndexError:
            raise IndexError(
                "A file with the name CDA_eICR.xml could not be found in zip file."
            )
    f = my_zipfile.open(file_to_open)
    return f.read().decode("utf-8")


def unzip_http(zipped_file) -> Dict:
    my_zipfile = ZipFile(zipped_file.file)
    try:
        file_to_open = [
            file for file in my_zipfile.namelist() if re.search("CDA_eICR.xml", file, re.I) in file
        ][0]
    except IndexError:
        raise IndexError(
            "A file with the name CDA_eICR.xml could not be found in zip file."
        )
    f = my_zipfile.open(file_to_open)
    return f.read().decode("utf-8")


def load_config_assets(upload_config_response_examples, PutConfigResponse) -> Dict:
    for status_code, file_name in upload_config_response_examples.items():
        upload_config_response_examples[status_code] = read_json_from_assets(file_name)
        # upload_config_response_examples[status_code]["model"] = PutConfigResponse
    return upload_config_response_examples
