import io
import json
import os
import pathlib
from functools import cache
from pathlib import Path
from typing import Dict
from typing import Optional
from zipfile import ZipFile

from dotenv import load_dotenv
from fastapi import UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

# Construct the path to the .env file
env_path = Path(__file__).resolve().parent.parent / ".env"

# Load the environment variables from your .env file
load_dotenv(dotenv_path=env_path)


@cache
def load_processing_config(config_name: str) -> dict:
    """
    Load a processing config given its name. Look in the 'custom_configs/' directory
    first. If no custom configs match the provided name, check the configs provided by
    default with this service in the 'default_configs/' directory.

    If necessary, it will also replace .env variables.

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

    # Replace placeholders with environment variable values
    replace_env_var_placeholders(processing_config)
    return processing_config


def replace_env_var_placeholders(config: dict) -> None:
    """
    Check for environment variable placeholders in the configuration
      and replace them if found.
    :param config: Loaded config json file that needs to be checked for replace vars.
    """
    # TODO: Currently, we are only replacing URLs, but may need to be
    # more generalizable in the future
    for settings in config.get("configurations", {}).values():
        if "url" in settings:
            settings["url"] = os.path.expandvars(settings["url"])


def read_json_from_assets(filename: str) -> Dict:
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


def load_json_from_binary(upload_file: UploadFile) -> Dict:
    """
    Helper method to transform a buffered IO of bytes into a json dictionary.
    """
    return json.load(io.BytesIO(upload_file.file.read()))


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


def search_for_file_in_zip(filename: str, zipfile: ZipFile) -> Optional[str]:
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


class CustomJSONResponse(JSONResponse):
    def __init__(self, content, url="", *args, **kwargs) -> None:
        super().__init__(content=jsonable_encoder(content), *args, **kwargs)
        self._content = content
        self.url = url

    def json(self) -> Dict:
        return self._content


def format_service_url(base_url: str, endpoint: str) -> str:
    """
    Simple helper function to construct an HTTP-accessable URL for a DIBBs
    building block, with correct quotation mark formatting.
    """
    url = base_url + endpoint
    url = url.replace('"', "")
    return url


def _socket_response_is_valid(**kwargs) -> bool:
    """
    Utility function that indicates whether a websocket endpoint can return
    data that the orchestration service processed. If the service sent back
    a 200, or the validation service verified the message's integrity, the
    socket can continue.
    """
    response = kwargs["response"]
    body = response.json()
    if "message_valid" in body:
        return body.get("message_valid")
    return response.status_code == 200
