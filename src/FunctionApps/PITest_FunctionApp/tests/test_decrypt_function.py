import os
from importlib.resources import files
import json
from pathlib import Path
import logging

import azure.functions as func
import pytest

from .. import DecryptFunction as dcf
from ..DecryptFunction.settings import Settings
from azure.storage.blob import BlobServiceClient, ContainerClient

# Fixtures run before each test and can be passed as arguments to individual tests to enable accessing the variables they define. More info: https://docs.pytest.org/en/latest/fixture.html#fixtures-scope-sharing-and-autouse-autouse-fixtures
@pytest.fixture(scope="session", autouse=True)
def initialize_env_vars():
    # get storage account settings
    storage_connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
    container_name = os.environ.get("STORAGE_CONTAINER")
    return storage_connection_string, container_name


@pytest.fixture(scope="session", autouse=True)
def local_settings():
    local_settings_path = files("DecryptFunction").parent / "local.settings.json"
    local_json_config = json.loads(local_settings_path.read_text())
    local_settings_vals = local_json_config.get("Values")
    settings = Settings()
    settings.private_key = local_settings_vals.get("PRIVATE_KEY")
    settings.private_key_password = local_settings_vals.get("PRIVATE_KEY_PASSWORD")
    # settings.azure_storage_connection_string = local_settings_vals.get("AZURE_STORAGE_CONNECTION_STRING")
    return settings


def test_decrypt_message(local_settings):
    test_file_path = (
        files("DecryptFunction").parent / "tests" / "assets" / "encrypted.txt"
    )
    blob_data = test_file_path.read_bytes()
    input_stream = func.blob.InputStream(data=blob_data, name="input test")
    result = dcf.decrypt_message(
        input_stream.read(),
        local_settings.private_key,
        local_settings.private_key_password,
    )
    assert result == b"TESTING EICR ENCRYPTION"


def test_trigger(local_settings):

    source_container_name = "raw"
    destination_container_name = "decrypted"
    source_container_client = ContainerClient.from_connection_string(
        local_settings.azure_storage_connection_string, source_container_name
    )
    destination_container_client = ContainerClient.from_connection_string(local_settings.azure_storage_connection_string, source_container_name
    )

    source_file_name = "encrypted.txt"
    destination_file_name = 
    test_file_path = files("DecryptFunction").parent / "tests" / "assets" / source_file_name

    with open(test_file_path, "rb") as data:
        blob_upload_result = source_container_client.upload_blob(name=source_file_name, data=data)
        properties = blob_upload_result.get_blob_properties()
        logging.properties(f"Post-source data upload blob Properties: {properties}")
        
        destination_blob_client = destination_container_client.get_blob_client(name=destination_file_name)
        while not destination_blob_client.exists():
            logging.info(f"Waiting for {destination_file_name} to be available in {destination_container_name}...")
        
        logging.info(f"{destination_file_name} available in {destination_container_name}. Downloading")

        destination_data = destination_blob_client.download_blob().readall()
        assert destination_data == b'TESTING EICR ENCRYPTION'
            
        
