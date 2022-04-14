import io

from unittest import mock

from GenerateCSVs.fhir import write_csvs, read_bundles_by_type, RECORD_TYPE_VXU


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


@mock.patch("GenerateCSVs.fhir.get_blobs")
def test_read_bundles_by_type(mock_get_blobs):
    container_url = "https://some-container"
    csv_input_prefix = "some-prefix"
    record_types = ["vxu", "elr", "ecr"]

    mock_get_blobs.return_value = iter(
        [
            ("VXU", io.BytesIO(b'{"resourceType":"Bundle", "id":"some-vxu-id"}')),
            ("ELR", io.BytesIO(b'{"resourceType":"Bundle", "id":"some-elr-id"}')),
        ]
    )

    bundles = read_bundles_by_type(container_url, csv_input_prefix, record_types)

    assert {
        ("VXU", "some-vxu-id"),
        ("ELR", "some-elr-id"),
    } == {(record_type, fhir.get("id")) for record_type, fhir in bundles}

    mock_get_blobs.assert_called_with(container_url, csv_input_prefix, record_types)
