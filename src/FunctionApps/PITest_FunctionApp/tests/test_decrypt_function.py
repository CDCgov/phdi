import json
import logging
import os
import uuid
from importlib.resources import files
from pathlib import Path

import azure.functions as func
import pytest
from azure.storage.blob import BlobServiceClient, ContainerClient

from .. import DecryptFunction as dcf
from ..DecryptFunction.settings import Settings


# This fixture runs before all tests and can be passed as arguments to individual tests to enable accessing the variables they define. 
# More info: https://docs.pytest.org/en/latest/fixture.html#fixtures-scope-sharing-and-autouse-autouse-fixtures
@pytest.fixture(scope="session", autouse=True)
def local_settings():
    # Note, we manually parse this file because it is not loaded automatically by the test runner
    local_settings_path = files("DecryptFunction").parent / "local.settings.json"
    local_json_config = json.loads(local_settings_path.read_text())
    local_settings_vals = local_json_config.get("Values")
    settings = Settings()
    settings.private_key = local_settings_vals.get("PRIVATE_KEY")
    settings.private_key_password = local_settings_vals.get("PRIVATE_KEY_PASSWORD")

    # Azurite connection string, from here: https://docs.microsoft.com/en-us/azure/storage/common/storage-use-azurite?tabs=visual-studio#http-connection-strings
    settings.azure_storage_connection_string = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
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

