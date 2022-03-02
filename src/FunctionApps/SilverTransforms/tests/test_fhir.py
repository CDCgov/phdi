from Transform.fhir import get_patient_records

from unittest import mock


@mock.patch("azure.storage.blob.ContainerClient.from_connection_string")
def test_get_patient_records(mock_client_init):
    mock_conn = mock.Mock()
    mock_conn.list_blobs.return_value = [{"props": "a"}]

    # Downloads the blob into bytes
    mock_blob = mock.Mock()
    mock_blob.content_as_bytes.return_value = b'{"name": "a"}\n{"name": "b"}'

    # Gets the blob itself
    mock_blob_client = mock.Mock()
    mock_blob_client.download_blob.return_value = mock_blob

    # Gets the blob client
    mock_conn.get_blob_client.return_value = mock_blob_client

    mock_client_init.return_value = mock_conn

    vals = get_patient_records("connstr", "container")

    assert [{"name": "a"}, {"name": "b"}] == list(vals)

    mock_conn.list_blobs.assert_called_with(name_starts_with="Patient")
    mock_conn.get_blob_client.assert_called_with({"props": "a"})
