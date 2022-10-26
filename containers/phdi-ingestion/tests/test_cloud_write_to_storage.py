import pathlib
import json
from fastapi.testclient import TestClient
from unittest import mock
from app.main import app

# from app.config import get_settings

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
    message = (
        "The data has successfully been stored in the azure cloud "
        "in test_bucket container with the name test_file_name."
    )
    assert actual_response.status_code == 200
    assert actual_response.json() == {"message": message}


def test_cloud_write_to_storage_missing_provider():
    test_request = {
        "blob": test_bundle,
        "cloud_provider": None,
        "bucket_name": "test_bucket",
        "file_name": "test_file_name",
    }

    expected_response = (
        "The following values are required, but were not included in "
        "the request and could not be read from the environment. "
        "Please resubmit the request including these values or add "
        "them as environment variables to this service. missing values: cloud_provider."
    )
    expected_status_code = 400
    actual_response = client.post(
        "/cloud/storage/write/write_blob_to_cloud_storage", json=test_request
    )
    assert actual_response.json() == expected_response
    assert actual_response.status_code == expected_status_code


def test_cloud_write_to_storage_wrong_provider():
    test_request = {
        "blob": test_bundle,
        "cloud_provider": "myprovider",
        "bucket_name": "test_bucket",
        "file_name": "test_file_name",
    }

    expected_detail_loc = "cloud_provider"
    expected_detail_msg = "unexpected value; permitted: 'azure', 'gcp'"
    expected_status_code = 422
    actual_response = client.post(
        "/cloud/storage/write/write_blob_to_cloud_storage", json=test_request
    )
    print(actual_response.json())
    print(actual_response)

    assert actual_response.json()["detail"][0]["loc"][1] == expected_detail_loc
    assert actual_response.json()["detail"][0]["msg"] == expected_detail_msg
    assert actual_response.status_code == expected_status_code


def test_cloud_write_to_storage_missing_bucket():
    test_request = {
        "blob": test_bundle,
        "cloud_provider": "azure",
        "bucket_name": None,
        "file_name": "test_file_name",
    }

    expected_response = (
        "The following values are required, but were not included in "
        "the request and could not be read from the environment. "
        "Please resubmit the request including these values or add "
        "them as environment variables to this service. missing values: bucket_name."
    )
    expected_status_code = 400
    actual_response = client.post(
        "/cloud/storage/write/write_blob_to_cloud_storage", json=test_request
    )
    assert actual_response.json() == expected_response
    assert actual_response.status_code == expected_status_code


def test_cloud_write_to_storage_missing_filename():
    test_request = {
        "blob": test_bundle,
        "cloud_provider": "azure",
        "bucket_name": "test_bucket",
        "file_name": None,
    }

    expected_response = (
        "The following values are required, but were not included in "
        "the request and could not be read from the environment. "
        "Please resubmit the request including these values or add "
        "them as environment variables to this service. missing values: file_name."
    )
    expected_status_code = 400
    actual_response = client.post(
        "/cloud/storage/write/write_blob_to_cloud_storage", json=test_request
    )
    print(actual_response.json())
    print(actual_response)
    assert actual_response.json() == expected_response
    assert actual_response.status_code == expected_status_code


def test_cloud_write_to_storage_missing_blob():
    test_request = {
        "blob": None,
        "cloud_provider": "azure",
        "bucket_name": "test_bucket",
        "file_name": "file_name",
    }

    expected_detail_msg = "none is not an allowed value"
    expected_detail_loc = "blob"
    expected_status_code = 422
    actual_response = client.post(
        "/cloud/storage/write/write_blob_to_cloud_storage", json=test_request
    )
    assert actual_response.json()["detail"][0]["msg"] == expected_detail_msg
    assert actual_response.json()["detail"][0]["loc"][1] == expected_detail_loc
    assert actual_response.status_code == expected_status_code
