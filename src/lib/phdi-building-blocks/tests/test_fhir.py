import io
import pytest
import polling
import requests

from datetime import datetime, timezone
from unittest import mock

from azure.identity import DefaultAzureCredential

from phdi_building_blocks.azure import AzureFhirServerCredentialManager
from phdi_building_blocks.fhir import (
    upload_bundle_to_fhir_server,
    export_from_fhir_server,
    _compose_export_url,
    download_from_export_response,
    log_fhir_server_error,
    fhir_server_get,
)


@mock.patch("phdi_building_blocks.fhir.log_fhir_server_error")
@mock.patch("requests.Session")
def test_upload_bundle_to_fhir_server(mock_requests_session, mock_log_error):
    mock_requests_session_instance = mock_requests_session.return_value

    mock_access_token_value = "some-token"
    mock_access_token = mock.Mock()
    mock_access_token.token = mock_access_token_value
    mock_cred_manager = mock.Mock()
    mock_cred_manager.get_access_token.return_value = mock_access_token

    mock_requests_return_value = mock.Mock(
        status_code=200,
        json=lambda: {
            "resourceType": "Bundle",
            "id": "some-id",
            "entry": [
                {
                    "resource": {"resourceType": "Patient", "id": "pat-id"},
                    "request": {"method": "PUT", "url": "Patient/pat-id"},
                    "response": {"status": "200 OK"},
                }
            ],
        },
    )
    mock_requests_session_instance.post.return_value = mock_requests_return_value

    response = upload_bundle_to_fhir_server(
        {
            "resourceType": "Bundle",
            "id": "some-id",
            "entry": [
                {
                    "resource": {"resourceType": "Patient", "id": "pat-id"},
                    "request": {"method": "PUT", "url": "Patient/pat-id"},
                }
            ],
        },
        mock_cred_manager,
        "https://some-fhir-url",
    )

    mock_requests_session_instance.post.assert_called_with(
        url="https://some-fhir-url",
        headers={
            "Authorization": f"Bearer {mock_access_token_value}",
            "Accept": "application/fhir+json",
            "Content-Type": "application/fhir+json",
        },
        json={
            "resourceType": "Bundle",
            "id": "some-id",
            "entry": [
                {
                    "resource": {"resourceType": "Patient", "id": "pat-id"},
                    "request": {"method": "PUT", "url": "Patient/pat-id"},
                }
            ],
        },
    )

    assert response == mock_requests_return_value
    mock_log_error.assert_not_called()


@mock.patch("phdi_building_blocks.fhir.log_fhir_server_error")
@mock.patch("requests.Session")
def test_upload_bundle_failure(mock_requests_session, mock_log_error):
    mock_requests_session_instance = mock_requests_session.return_value

    mock_access_token_value = "some-token"
    mock_access_token = mock.Mock()
    mock_access_token.token = mock_access_token_value
    mock_cred_manager = mock.Mock()
    mock_cred_manager.get_access_token.return_value = mock_access_token

    mock_requests_return_value = mock.Mock(
        status_code=400,
        json=lambda: {
            "resourceType": "OperationOutcome",
            "severity": "error",
        },
    )

    mock_requests_session_instance.post.return_value = mock_requests_return_value

    response = upload_bundle_to_fhir_server(
        {
            "resourceType": "Bundle",
            "id": "some-id",
            "entry": [
                {
                    "resource": {"resourceType": "Patient", "id": "pat-id"},
                    "request": {"method": "PUT", "url": "Patient/pat-id"},
                }
            ],
        },
        mock_cred_manager,
        "https://some-fhir-url",
    )

    mock_requests_session_instance.post.assert_called_with(
        url="https://some-fhir-url",
        headers={
            "Authorization": f"Bearer {mock_access_token_value}",
            "Accept": "application/fhir+json",
            "Content-Type": "application/fhir+json",
        },
        json={
            "resourceType": "Bundle",
            "id": "some-id",
            "entry": [
                {
                    "resource": {"resourceType": "Patient", "id": "pat-id"},
                    "request": {"method": "PUT", "url": "Patient/pat-id"},
                }
            ],
        },
    )

    assert response == mock_requests_return_value
    mock_log_error.assert_called_with(400)
    assert mock_log_error.call_count == 1


@mock.patch("phdi_building_blocks.fhir.log_fhir_server_error")
@mock.patch("requests.Session")
def test_upload_bundle_partial_failure(mock_requests_session, mock_log_error):
    mock_requests_session_instance = mock_requests_session.return_value

    mock_access_token_value = "some-token"
    mock_access_token = mock.Mock()
    mock_access_token.token = mock_access_token_value
    mock_cred_manager = mock.Mock()
    mock_cred_manager.get_access_token.return_value = mock_access_token

    mock_requests_return_value = mock.Mock(
        status_code=200,
        json=lambda: {
            "resourceType": "Bundle",
            "entry": [
                {
                    "resource": {"resourceType": "Patient"},
                    "response": {"status": "200 OK"},
                },
                {
                    "resource": {"resourceType": "Organization"},
                    "response": {"status": "400 Bad Request"},
                },
                {
                    "resource": {"resourceType": "Vaccination"},
                    "response": {"status": "200 OK"},
                },
            ],
        },
    )

    mock_requests_session_instance.post.return_value = mock_requests_return_value

    response = upload_bundle_to_fhir_server(
        {
            "resourceType": "Bundle",
            "id": "some-id",
            "entry": [
                {
                    "resource": {"resourceType": "Patient", "id": "pat-id"},
                    "request": {"method": "PUT", "url": "Patient/pat-id"},
                }
            ],
        },
        mock_cred_manager,
        "https://some-fhir-url",
    )

    mock_requests_session_instance.post.assert_called_with(
        url="https://some-fhir-url",
        headers={
            "Authorization": f"Bearer {mock_access_token_value}",
            "Accept": "application/fhir+json",
            "Content-Type": "application/fhir+json",
        },
        json={
            "resourceType": "Bundle",
            "id": "some-id",
            "entry": [
                {
                    "resource": {"resourceType": "Patient", "id": "pat-id"},
                    "request": {"method": "PUT", "url": "Patient/pat-id"},
                }
            ],
        },
    )

    assert response == mock_requests_return_value
    mock_log_error.assert_called_with(status_code=400, batch_entry_index=1)
    assert mock_log_error.call_count == 1


@mock.patch.object(DefaultAzureCredential, "get_token")
def test_get_access_token_reuse(mock_get_token):

    mock_access_token = mock.Mock()
    mock_access_token.token = "my-token"
    mock_access_token.expires_on = datetime.now(timezone.utc).timestamp() + 2399

    mock_get_token.return_value = mock_access_token

    fhirserver_cred_manager = AzureFhirServerCredentialManager("https://fhir-url")
    token1 = fhirserver_cred_manager.get_access_token()

    # Use the default token reuse tolerance, which is less than
    # the mock token's time to live of 2399
    fhirserver_cred_manager.get_access_token()
    mock_get_token.assert_called_once_with("https://fhir-url/.default")
    assert token1.token == "my-token"


@mock.patch.object(DefaultAzureCredential, "get_token")
def test_get_access_token_refresh(mock_get_token):

    mock_access_token = mock.Mock()
    mock_access_token.token = "my-token"
    mock_access_token.expires_on = datetime.now(timezone.utc).timestamp() + 2399

    mock_get_token.return_value = mock_access_token

    fhirserver_cred_manager = AzureFhirServerCredentialManager("https://fhir-url")
    token1 = fhirserver_cred_manager.get_access_token()

    # This time, use a very high token reuse tolerance to
    # force another refresh for the new call
    fhirserver_cred_manager.get_access_token(2500)
    mock_get_token.assert_has_calls(
        [mock.call("https://fhir-url/.default"), mock.call("https://fhir-url/.default")]
    )
    assert token1.token == "my-token"


@mock.patch("requests.Session")
def test_export_from_fhir_server(mock_requests_session):
    mock_requests_session_instance = mock_requests_session.return_value

    mock_access_token_value = "some-token"
    mock_access_token = mock.Mock()
    mock_access_token.token = mock_access_token_value
    mock_cred_manager = mock.Mock()
    mock_cred_manager.get_access_token.return_value = mock_access_token

    fhir_url = "https://fhir-url"

    poll_step = 0.1
    poll_timeout = 0.5

    mock_export_response = mock.Mock()
    mock_export_response.status_code = 202

    mock_export_response.headers = {"Content-Location": "https://export-download-url"}

    mock_export_download_response_accepted = mock.Mock()
    mock_export_download_response_accepted.status_code = 202

    mock_export_download_response_ok = mock.Mock()
    mock_export_download_response_ok.status_code = 200
    mock_export_download_response_ok.json.return_value = {
        "output": [
            {"type": "Patient", "url": "https://export-download-url/_Patient"},
            {"type": "Observation", "url": "https://export-download-url/_Observation"},
        ]
    }

    mock_requests_session_instance.get.side_effect = [
        mock_export_response,
        mock_export_download_response_accepted,
        mock_export_download_response_accepted,
        mock_export_download_response_accepted,
        mock_export_download_response_ok,
    ]

    export_from_fhir_server(
        cred_manager=mock_cred_manager,
        fhir_url=fhir_url,
        poll_step=poll_step,
        poll_timeout=poll_timeout,
    )

    mock_requests_session_instance.get.assert_has_calls(
        [
            mock.call(
                url=f"{fhir_url}/$export",
                headers={
                    "Authorization": f"Bearer {mock_access_token_value}",
                    "Accept": "application/fhir+json",
                    "Prefer": "respond-async",
                },
            ),
            mock.call(
                url="https://export-download-url",
                headers={
                    "Authorization": f"Bearer {mock_access_token_value}",
                    "Accept": "application/fhir+ndjson",
                },
            ),
            mock.call(
                url="https://export-download-url",
                headers={
                    "Authorization": f"Bearer {mock_access_token_value}",
                    "Accept": "application/fhir+ndjson",
                },
            ),
            mock.call(
                url="https://export-download-url",
                headers={
                    "Authorization": f"Bearer {mock_access_token_value}",
                    "Accept": "application/fhir+ndjson",
                },
            ),
            mock.call(
                url="https://export-download-url",
                headers={
                    "Authorization": f"Bearer {mock_access_token_value}",
                    "Accept": "application/fhir+ndjson",
                },
            ),
        ]
    )
    assert mock_requests_session_instance.get.call_count == 5


@mock.patch("requests.Session")
def test_export_from_fhir_server_timeout(mock_requests_session):
    mock_requests_session_instance = mock_requests_session.return_value

    mock_access_token_value = "some-token"
    mock_access_token = mock.Mock()
    mock_access_token.token = mock_access_token_value
    mock_cred_manager = mock.Mock()
    mock_cred_manager.get_access_token.return_value = mock_access_token

    fhir_url = "https://fhir-url"

    poll_step = 0.1
    poll_timeout = 0.5

    mock_export_response = mock.Mock()
    mock_export_response.status_code = 202

    mock_export_response.headers = {"Content-Location": "https://export-download-url"}

    mock_export_download_response_accepted = mock.Mock()
    mock_export_download_response_accepted.status_code = 202

    mock_requests_session_instance.get.side_effect = [
        mock_export_response,
        mock_export_download_response_accepted,
        mock_export_download_response_accepted,
        mock_export_download_response_accepted,
        mock_export_download_response_accepted,
        mock_export_download_response_accepted,
        mock_export_download_response_accepted,
    ]

    with pytest.raises(polling.TimeoutException):
        export_from_fhir_server(
            cred_manager=mock_cred_manager,
            fhir_url=fhir_url,
            poll_step=poll_step,
            poll_timeout=poll_timeout,
        )

    assert mock_requests_session_instance.get.call_count == 7


@mock.patch("requests.Session")
def test_export_from_fhir_server_error(mock_requests_session):
    mock_requests_session_instance = mock_requests_session.return_value

    mock_access_token_value = "some-token"
    mock_access_token = mock.Mock()
    mock_access_token.token = mock_access_token_value
    mock_cred_manager = mock.Mock()
    mock_cred_manager.get_access_token.return_value = mock_access_token

    fhir_url = "https://fhir-url"

    poll_step = 0.1
    poll_timeout = 0.5

    mock_export_response = mock.Mock()
    mock_export_response.status_code = 202

    mock_export_response.headers = {"Content-Location": "https://export-download-url"}

    mock_export_download_response_error = mock.Mock()
    mock_export_download_response_error.status_code = 500

    mock_requests_session_instance.get.side_effect = [
        mock_export_response,
        mock_export_download_response_error,
    ]

    with pytest.raises(requests.HTTPError):
        export_from_fhir_server(
            cred_manager=mock_cred_manager,
            fhir_url=fhir_url,
            poll_step=poll_step,
            poll_timeout=poll_timeout,
        )

    assert mock_requests_session_instance.get.call_count == 2


def test_compose_export_url():
    fhir_url = "https://fhir-url"
    assert _compose_export_url(fhir_url) == f"{fhir_url}/$export"
    assert _compose_export_url(fhir_url, "Patient") == f"{fhir_url}/Patient/$export"
    assert (
        _compose_export_url(fhir_url, "Group/group-id")
        == f"{fhir_url}/Group/group-id/$export"
    )
    assert (
        _compose_export_url(fhir_url, "Patient", "2022-01-01T00:00:00Z")
        == f"{fhir_url}/Patient/$export?_since=2022-01-01T00:00:00Z"
    )
    assert (
        _compose_export_url(
            fhir_url, "Patient", "2022-01-01T00:00:00Z", "Patient,Observation"
        )
        == f"{fhir_url}/Patient/$export?_since=2022-01-01T00:00:00Z"
        + "&_type=Patient,Observation"
    )
    assert (
        _compose_export_url(
            fhir_url,
            "Patient",
            "2022-01-01T00:00:00Z",
            "Patient,Observation",
            "some-container",
        )
        == f"{fhir_url}/Patient/$export?_since=2022-01-01T00:00:00Z"
        + "&_type=Patient,Observation&_container=some-container"
    )
    assert (
        _compose_export_url(fhir_url, "Patient", None, "Patient,Observation")
        == f"{fhir_url}/Patient/$export?_type=Patient,Observation"
    )

    with pytest.raises(ValueError):
        _compose_export_url(fhir_url, "InvalidExportScope")


@mock.patch("phdi_building_blocks.fhir._download_export_blob")
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

    for type, output in download_from_export_response(export_response=export_response):
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
            mock.call(blob_url="https://export-download-url/_Patient"),
            mock.call(blob_url="https://export-download-url/_Observation"),
        ]
    )


@mock.patch("phdi_building_blocks.fhir.logging")
def test_log_fhir_server_error(patched_logger):

    log_fhir_server_error(200)
    assert ~patched_logger.error.called

    error_status_codes = {
        401: "FHIR SERVER ERROR - Status Code 401: Failed to authenticate.",
        403: "FHIR SERVER ERROR - Status Code 403: User does not have permission to make that request.",  # noqa
        404: "FHIR SERVER ERROR - Status Code 404: Server or requested data not found.",
        410: "FHIR SERVER ERROR - Status Code 410: Server has deleted this cached data.",  # noqa
        499: "FHIR SERVER ERROR - Status code 499",
        599: "FHIR SERVER ERROR - Status code 599",
    }

    for status_code, error_message in error_status_codes.items():
        log_fhir_server_error(status_code)
        patched_logger.error.assert_called_with(error_message)


@mock.patch("phdi_building_blocks.fhir.logging")
def test_log_fhir_server_error_batch(patched_logger):

    log_fhir_server_error(200)
    assert ~patched_logger.error.called

    error_status_codes = {
        401: "FHIR SERVER ERROR in zero-based message index 0 of FHIR batch - "
        + "Status Code 401: Failed to authenticate.",
        403: "FHIR SERVER ERROR in zero-based message index 1 of FHIR batch - "
        + "Status Code 403: User does not have permission to make that request.",
        404: "FHIR SERVER ERROR in zero-based message index 2 of FHIR batch - "
        + "Status Code 404: Server or requested data not found.",
        410: "FHIR SERVER ERROR in zero-based message index 3 of FHIR batch - "
        + "Status Code 410: Server has deleted this cached data.",
        499: "FHIR SERVER ERROR in zero-based message index 4 of FHIR batch - "
        + "Status code 499",
        599: "FHIR SERVER ERROR in zero-based message index 5 of FHIR batch - "
        + "Status code 599",
    }

    for batch_index, (status_code, error_message) in enumerate(
        error_status_codes.items()
    ):
        log_fhir_server_error(status_code=status_code, batch_entry_index=batch_index)
        patched_logger.error.assert_called_with(error_message)


@mock.patch("phdi_building_blocks.fhir.log_fhir_server_error")
@mock.patch("requests.Session")
def test_fhir_server_get(patched_requests_session, patched_logger):
    mock_requests_session_instance = patched_requests_session.return_value

    mock_access_token_value = "some-token"
    mock_access_token = mock.Mock()
    mock_access_token.token = mock_access_token_value
    mock_cred_manager = mock.Mock()
    mock_cred_manager.get_access_token.return_value = mock_access_token

    url = "url_for_FHIR_server_get_request"

    fhir_server_get(url, mock_cred_manager)

    header = {"Authorization": f"Bearer {mock_access_token_value}"}
    mock_requests_session_instance.get.assert_called_with(url=url, headers=header)

    response = mock_requests_session_instance.get(url=url, headers=header)
    patched_logger.assert_called_with(response.status_code)
