import pathlib
import json
from fastapi.testclient import TestClient
from unittest import mock

from app.main import app
#from app.config import get_settings

client = TestClient(app)

test_bundle = json.load(
    open(pathlib.Path(__file__).parent / "assets" / "single_patient_bundle.json")
)


@mock.patch("app.routers.cloud_write_to_storage.get_cloud_provider_storage_connection")
@mock.patch("app.routers.cloud_write_to_storage.write_blob_to_cloud_storage_endpoint")
def test_cloud_write_to_storage_params_success(
    patched_blob_write, patched_get_provider
):
    test_request = {
        "blob": test_bundle,
        "cloud_provider": "azure",
        "bucket_name": "test_bucket",
        "file_name": "test_file_name",
    }

    patched_get_provider("azure").return_value = mock.Mock()
    
        #     message=input,
        #     container_name=input["bucket_name"],
        #     filename=input["file_name"],
        # )

    cloud_response = mock.Mock()
    cloud_response.status_code = 200
    cloud_response.json.return_value = ""
    patched_blob_write.return_value = cloud_response

    patched_get_provider.return_value.upload_object.return_value = mock.Mock()

    actual_response = client.post(
        "/cloud/storage/write/write_blob_to_cloud_storage", json=test_request
    )

    patched_get_provider.return_value.upload_object.assert_called_with(
        message=test_request,
        container_name="test_bucket",
        filename="test_file_name",
    )
    assert actual_response.status_code == 200
    assert actual_response.json() == {
        "message": "The data has successfully been stored in the azure cloud in test_bucket container with the name test_file_name."
    }
