import json
import pathlib
from fastapi import UploadFile
from functools import cache
from pathlib import Path
from typing import Dict
from zipfile import ZipFile
import io


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


def unzip_ws(file_bytes) -> Dict:
    zipfile = ZipFile(io.BytesIO(file_bytes), "r")
    if zipfile.namelist():
        return search_for_ecr_data(zipfile)
    else:
        raise FileNotFoundError("This is not a valid .zip file.")


def unzip_http(upload_file: UploadFile) -> Dict:
    zipped_file = ZipFile(io.BytesIO(upload_file.file.read()), "r")
    return search_for_ecr_data(zipped_file)


def search_for_ecr_data(valid_zipfile: ZipFile) -> Dict:
    return_data = {}

    ecr_reference = search_for_file_in_zip("CDA_eICR.xml", valid_zipfile)
    if ecr_reference is None:
        raise IndexError("There is no eICR in this zip file.")

    ecr = valid_zipfile.open(ecr_reference)
    ecr_data = ecr.read().decode("utf-8")
    return_data["ecr"] = ecr_data

    # RR data is optionally present
    rr_reference = search_for_file_in_zip("CDA_RR.xml", valid_zipfile)
    if rr_reference:
        rr = valid_zipfile.open(rr_reference)
        rr_data = rr.read().decode("utf-8")
        return_data["rr"] = rr_data

    return return_data


def search_for_file_in_zip(filename, zipfile):
    results = [file for file in zipfile.namelist() if filename in file]
    if results:
        return results[0]
    else:
        return None


def load_config_assets(upload_config_response_examples, PutConfigResponse) -> Dict:
    for status_code, file_name in upload_config_response_examples.items():
        upload_config_response_examples[status_code] = read_json_from_assets(file_name)
        # upload_config_response_examples[status_code]["model"] = PutConfigResponse
    return upload_config_response_examples
