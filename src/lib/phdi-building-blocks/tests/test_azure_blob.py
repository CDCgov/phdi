import os
from unittest import mock

from phdi_building_blocks.azure_blob import store_data


@mock.patch("phdi_building_blocks.azure_blob.get_blob_client")
def test_store_data(mock_get_client):
    mock_blob = mock.Mock()

    mock_client = mock.Mock()
    mock_client.get_blob_client.return_value = mock_blob

    mock_get_client.return_value = mock_client

    store_data(
        "some-url",
        "output/path",
        "some-filename-1.fhir",
        "some-bundle-type",
        {"hello": "world"},
    )

    mock_client.get_blob_client.assert_called_with(
        os.path.normpath("output/path/some-bundle-type/some-filename-1.fhir")
    )
    mock_blob.upload_blob.assert_called()
