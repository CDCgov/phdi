from unittest import mock

import pytest

from phdi.fhir.cloud.azure import download_from_fhir_export_response


@mock.patch("phdi.fhir.cloud.azure.download_blob_from_url")
def test_download_from_export_response(mock_download_blob_from_url):
    download_iterator = iter(
        [
            b'{"resourceType": "Patient", "id": "some-id"}\n'
            + b'{"resourceType": "Patient", "id": "some-id2"}\n',
            b'{"resourceType": "Observation", "id": "some-id"}\n'
            + b'{"resourceType": "Observation", "id": "some-id2"}\n',
        ]
    )
    mock_download_blob_from_url.side_effect = (
        lambda blob_url, output, credential: output.write(next(download_iterator))
    )

    export_response = {
        "output": [
            {"type": "Patient", "url": "https://export-download-url/_Patient"},
            {
                "type": "Observation",
                "url": "https://export-download-url/_Observation",
            },
        ]
    }

    mock_cred_manager = mock.Mock()
    mock_cred_manager.get_access_token.return_value = "some-token"

    patient_count = 0
    observation_count = 0
    for type, output in download_from_fhir_export_response(
        cred_manager=mock_cred_manager, export_response=export_response
    ):
        if type == "Patient":
            patient_count += 1
            assert (
                output.read()
                == '{"resourceType": "Patient", "id": "some-id"}\n'
                + '{"resourceType": "Patient", "id": "some-id2"}\n'
            )
        elif type == "Observation":
            observation_count += 1
            assert (
                output.read()
                == '{"resourceType": "Observation", "id": "some-id"}\n'
                + '{"resourceType": "Observation", "id": "some-id2"}\n'
            )

    assert patient_count == 1
    assert observation_count == 1


def test_download_from_export_response_empty():
    export_response = {"output": []}

    mock_cred_manager = mock.Mock()
    mock_cred_manager.get_access_token.return_value = "some-token"

    download_iterator = download_from_fhir_export_response(
        cred_manager=mock_cred_manager, export_response=export_response
    )

    with pytest.raises(StopIteration):
        next(download_iterator)
