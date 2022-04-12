import io

from unittest import mock

from GenerateCSVs.fhir import write_csvs, RECORD_TYPE_VXU


@mock.patch("GenerateCSVs.fhir.get_container_client")
def test_write_csvs(mock_get_container):
    container = mock.Mock()
    blob = mock.Mock()
    container.get_blob_client.return_value = blob
    mock_get_container.return_value = container

    write_csvs(
        "some-url",
        "some-prefix",
        {
            RECORD_TYPE_VXU: io.StringIO("hello,world"),
        },
    )

    mock_get_container.assert_called_with("some-url")
    container.get_blob_client.assert_called_with("some-prefix/vxu.csv")
    blob.upload_blob.assert_called_with(b"hello,world")
