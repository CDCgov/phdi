import io
import json

from unittest import mock

from IntakePipeline.fhir import read_fhir_bundles, get_blobs, store_bundle

from azure.storage.blob import BlobProperties


@mock.patch("IntakePipeline.fhir.get_blob_client")
def test_get_blobs(mock_get_client):
    mock_client = mock.Mock()

    folderblob = BlobProperties()
    folderblob.name = "afolder"
    folderblob.size = 0

    jsonblob = BlobProperties()
    jsonblob.name = "afolder/afile.json"
    jsonblob.size = 1000

    otherblob = BlobProperties()
    otherblob.name = "afolder/bfile.json"
    otherblob.size = 512

    # Actually returns an azure.core.paging.ItemPaged, which is basically an iterator
    mock_client.list_blobs.return_value = [folderblob, jsonblob, otherblob]
    mock_get_client.return_value = mock_client

    # return the first, then the second record on their resp calls
    mock_blob = mock.Mock()
    mock_blob.content_as_bytes.side_effect = [b'{"record": "a"}', b'{"record": "b"}']

    mock_blob_client = mock.Mock()
    mock_blob_client.download_blob.return_value = mock_blob
    mock_client.get_blob_client.return_value = mock_blob_client

    files = list(get_blobs("some-url", "some-prefix"))

    assert len(files) == 2
    assert json.load(files[0]).get("record") == "a"
    assert json.load(files[1]).get("record") == "b"

    mock_get_client.assert_called_with("some-url")
    mock_client.list_blobs.assert_called_with(name_starts_with="some-prefix")


@mock.patch("IntakePipeline.fhir.get_blob_client")
@mock.patch("IntakePipeline.fhir.uuid")
def test_store_bundle(mock_uuid, mock_get_client):
    mock_uuid.uuid4.return_value = "some-uuid"

    mock_blob = mock.Mock()

    mock_client = mock.Mock()
    mock_client.get_blob_client.return_value = mock_blob

    mock_get_client.return_value = mock_client

    store_bundle("some-url", "output/path", {"hello": "world"})

    mock_client.get_blob_client.assert_called_with("output/path/some-uuid.fhir")
    mock_blob.upload_blob.assert_called()


@mock.patch("IntakePipeline.fhir.get_blobs")
def test_read_fhir_bundles(mock_get_blobs):
    # Make sure we correctly deal with garbage too
    mock_get_blobs.return_value = iter(
        [
            io.BytesIO(b'{"id": "first"}'),
            io.BytesIO(b"MSH|WHO|PUT|HL7|IN^HERE^^^||||||"),
            io.BytesIO(b'{"id": "second"}'),
        ]
    )

    bundles = read_fhir_bundles("some-url", "some-prefix")
    assert {"first", "second"} == {r.get("id") for r in bundles}
