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
from fastapi import Response
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
    # TODO: We might be able to delete this function since we store URLs
    # in actual env variables now, not in configs anymore
    for settings in config.get("configurations", {}).values():
        if "url" in settings:
            settings["url"] = os.path.expandvars(settings["url"])


def read_json_from_assets(filename: str) -> Dict:
    """
    Loads a JSON file from the 'assets' directory.

    :param filename: Name of the JSON file to load.
    :return: Parsed JSON content as a dictionary.
    """
    return json.load(open((pathlib.Path(__file__).parent.parent / "assets" / filename)))


def unzip_ws(file_bytes) -> Dict:
    """
    Extracts and processes data from a zip file's bytes.

    :param file_bytes: Bytes of the zip file to be processed.
    :return: Processed data from the zip file.
    """
    zipfile = ZipFile(io.BytesIO(file_bytes), "r")
    if zipfile.namelist():
        return search_for_ecr_data(zipfile)
    else:
        raise FileNotFoundError("This is not a valid .zip file.")


def unzip_http(upload_file: UploadFile) -> Dict:
    """
    Extracts and processes ECR data from an uploaded zip file.

    :param upload_file: The uploaded zip file.
    :return: ECR data extracted from the zip file.
    """
    zipped_file = ZipFile(io.BytesIO(upload_file.file.read()), "r")
    return search_for_ecr_data(zipped_file)


def load_json_from_binary(upload_file: UploadFile) -> Dict:
    """
    Helper method to transform a buffered IO of bytes into a json dictionary.
    """
    return json.load(io.BytesIO(upload_file.file.read()))


def search_for_ecr_data(valid_zipfile: ZipFile) -> Dict:
    """
    Searches for and extracts eICR and optional RR data from a valid zip file.

    :param valid_zipfile: A ZipFile object to search within.
    :return: Contains 'ecr' data as a mandatory key, and 'rr' data if present.
    """
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
    """
    Searches for a file by name within a zip file.

    :param filename: The name of the file to search for.
    :param zipfile: The zip file to search within.
    :return: The name of the first matching file, or None if not found.
    """
    results = [file for file in zipfile.namelist() if filename in file]
    if results:
        return results[0]
    else:
        return None


def load_config_assets(upload_config_response_examples, PutConfigResponse) -> Dict:
    """
    Loads JSON config assets, updating the input dict in place.

    :param upload_config_response_examples: Status codes to JSON filenames.
    :param PutConfigResponse: Intended for future use or extension.
    :return: Updated with loaded JSON content.
    """
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
        """
        Returns the JSON content as a dictionary.

        :return: The content of the JSON.
        """
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


def _combine_response_bundles(
    response: Response, responses: dict, processing_config: dict
):
    """
    Loop through the output element of the config and add them to the
    response object. If output element isn't in config, just return default
    """
    default_response = response.json()
    if "outputs" not in processing_config:
        return default_response
    resp = []
    config = [
        obj
        for obj in processing_config["workflow"]
        if "name" in obj and obj["name"] in processing_config["outputs"]
    ]
    for step in config:
        resp.append({step["name"]: responses[step["service"]].json()})

    if ("default-response" in processing_config) and (
        not processing_config["default-response"]
    ):
        return {"responses": resp}
    else:
        return {**default_response, "responses": resp}
