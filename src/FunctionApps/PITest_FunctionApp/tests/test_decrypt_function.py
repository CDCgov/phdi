import json
from importlib.resources import files


import azure.functions as func
import pgpy.errors
import pytest

from .. import DecryptFunction as dcf
from ..DecryptFunction.settings import DecryptSettings


# This fixture runs before all tests and can be passed as arguments to individual tests to enable accessing the variables they define. 
# More info: https://docs.pytest.org/en/latest/fixture.html#fixtures-scope-sharing-and-autouse-autouse-fixtures
@pytest.fixture(scope="session", autouse=True)
def local_settings() -> DecryptSettings:
    """Local settings relevant for running these tests.
    Note, unlike running the function itself, we manually parse this file,
    because it is not loaded automatically by the test runner.

    Returns:
        DecryptSettings: settings object describing relevant subset of settings for this function
    """
    local_settings_path = (
        files("DecryptFunction").parent / "tests" / "assets" / "test.settings.json"
    )
    local_json_config = json.loads(local_settings_path.read_text())
    local_settings_vals = local_json_config.get("Values")
    settings = DecryptSettings()
    settings.private_key = local_settings_vals.get("PRIVATE_KEY")
    settings.private_key_password = local_settings_vals.get("PRIVATE_KEY_PASSWORD")

    # Uses dummy Azurite connection string, from here: https://docs.microsoft.com/en-us/azure/storage/common/storage-use-azurite?tabs=visual-studio#http-connection-strings
    settings.azure_storage_connection_string = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
    return settings


def test_decrypt_message_success(local_settings):
    """Tests decrypting a message using a specified private key in base64 encoded format.

    Args:
        local_settings ([type]): passed automatically via above fixture
    """
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


def test_decrypt_message_failure_wrong_receiver(local_settings):
    """Attempt to decrypt a message that was not intended for us.

    Args:
        local_settings ([type]): passed automatically via above fixture
    """
    test_file_path = (
        files("DecryptFunction").parent
        / "tests"
        / "assets"
        / "encrypted_to_someone_else.txt"
    )
    blob_data = test_file_path.read_bytes()
    input_stream = func.blob.InputStream(data=blob_data, name="input test")

    with pytest.raises(pgpy.errors.PGPError) as exc_info:
        dcf.decrypt_message(
            input_stream.read(),
            local_settings.private_key,
            local_settings.private_key_password,
        )

    assert "Cannot decrypt the provided message with this key" in str(exc_info.value)
