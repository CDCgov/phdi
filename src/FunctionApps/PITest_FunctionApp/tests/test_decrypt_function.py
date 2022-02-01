import os
from importlib.resources import files
import json
from pathlib import Path

import azure.functions as func
import pytest

from .. import DecryptFunction as dcf
from ..DecryptFunction.settings import Settings


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
    settings.azure_storage_connection_string = local_settings_vals.get("AZURE_STORAGE_CONNECTION_STRING")
    return settings

def test_decrypt_message(local_settings):
    test_file_path = files("DecryptFunction").parent / "tests" / "assets" / "encrypted.txt"
    blob_data = test_file_path.read_bytes()
    input_stream = func.blob.InputStream(data=blob_data, name='input test')
    result = dcf.decrypt_message(input_stream.read(), local_settings.private_key, local_settings.private_key_password)
    assert result == b'TESTING EICR ENCRYPTION'

