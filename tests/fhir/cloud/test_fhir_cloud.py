import io

from phdi.fhir.cloud.azure import download_from_fhir_export_response
from unittest import mock


@mock.patch("phdi.fhir.cloud.azure._download_export_blob")
def test_download_from_export_response(mock_download_export_blob):
    mock_download_export_blob.side_effect = [
        io.TextIOWrapper(
            io.BytesIO(
                b'{"resourceType": "Patient", "id": "some-id"}\n'
                + b'{"resourceType": "Patient", "id": "some-id2"}\n'
            ),
            encoding="utf-8",
            newline="\n",
        ),
        io.TextIOWrapper(
            io.BytesIO(
                b'{"resourceType": "Observation", "id": "some-id"}\n'
                + b'{"resourceType": "Observation", "id": "some-id2"}\n'
            ),
            encoding="utf-8",
            newline="\n",
        ),
    ]

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

    for type, output in download_from_fhir_export_response(
        cred_manager=mock_cred_manager, export_response=export_response
    ):
        if type == "Patient":
            assert (
                output.read()
                == '{"resourceType": "Patient", "id": "some-id"}\n'
                + '{"resourceType": "Patient", "id": "some-id2"}\n'
            )
        elif type == "Observation":
            assert (
                output.read()
                == '{"resourceType": "Observation", "id": "some-id"}\n'
                + '{"resourceType": "Observation", "id": "some-id2"}\n'
            )

    mock_download_export_blob.assert_has_calls(
        [
            mock.call(
                blob_url="https://export-download-url/_Patient",
                cred_manager=mock_cred_manager,
            ),
            mock.call(
                blob_url="https://export-download-url/_Observation",
                cred_manager=mock_cred_manager,
            ),
        ]
    )
