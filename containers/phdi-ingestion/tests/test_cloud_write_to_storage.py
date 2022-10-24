import os
import pathlib
import json
import copy
from fastapi.testclient import TestClient
from unittest import mock

from app.main import app
from app.config import get_settings

client = TestClient(app)

test_bundle = json.load(
    open(pathlib.Path(__file__).parent / "assets" / "single_patient_bundle.json")
)


@mock.patch("app.routers.cloud_write_to_storage.write_blob_to_cloud_storage")
@mock.patch("app.routers.cloud_write_to_storage.get_cloud_provider_storage_connection")
def test_cloud_write_to_storage_params_success(
    patched_azure_storage, patched_blob_write
):
    test_request = {
        "blob": test_bundle,
        "cloud_provider": "azure",
        "bucket_name": "test_bucket",
        "file_name": "test_file_name",
    }

    patched_azure_storage.return_value = mock.Mock()

    cloud_response = mock.Mock()
    cloud_response.status_code = 200
    cloud_response.json.return_value = ""
    patched_blob_write.return_value = cloud_response

    actual_response = client.post(
        "/cloud/storage/write/write_blob_to_cloud_storage", json=test_request
    )

    patched_blob_write.assert_called_with(
        blob=test_bundle,
        cloud_provider=patched_azure_storage(),
        bucket_name="test_bucket",
        file_name="test_file_name",
    )
    assert actual_response.status_code == 200
    assert actual_response.json() == {
        "message": "The data has successfully been stored in the azure cloud in test_bucket container with the name test_file_name."
    }
