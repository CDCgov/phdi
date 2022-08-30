import polling
import pytest
import requests

from phdi.fhir.transport import http_request_with_reauth, export_from_fhir_server
from phdi.fhir.transport.export import _compose_export_url
from unittest import mock


@mock.patch("requests.Session")
def test_auth_retry(patched_requests_session):
    mock_requests_session_instance = patched_requests_session.return_value

    response_content = '{"resourceType": "Patient", "id": "some-id"}'

    mock_requests_session_instance.get.side_effect = [
        mock.Mock(status_code=401),
        mock.Mock(status_code=200, text=response_content),
    ]

    mock_access_token_value1 = "some-token1"
    mock_access_token_value2 = "some-token2"

    mock_cred_manager = mock.Mock()
    mock_cred_manager.get_access_token.side_effect = [
        mock_access_token_value1,
        mock_access_token_value2,
    ]

    url = "https://fhir-url"

    initial_access_token = mock_cred_manager.get_access_token()
    response = http_request_with_reauth(
        cred_manager=mock_cred_manager,
        url=url,
        retry_count=3,
        request_type="GET",
        allowed_methods=["GET"],
        headers={"Authorization": f"Bearer {initial_access_token}"},
    )

    assert response.status_code == 200
    assert response.text == response_content

    mock_cred_manager.get_access_token.call_count == 2

    mock_requests_session_instance.get.assert_called_with(
        url=url, headers={"Authorization": f"Bearer {mock_access_token_value2}"}
    )
    mock_requests_session_instance.get.call_count == 2


@mock.patch("requests.Session")
def test_auth_retry_double_fail(patched_requests_session):
    mock_requests_session_instance = patched_requests_session.return_value

    mock_requests_session_instance.get.side_effect = [
        mock.Mock(status_code=401),
        mock.Mock(status_code=401),
    ]

    mock_access_token_value1 = "some-token1"
    mock_access_token_value2 = "some-token2"

    mock_cred_manager = mock.Mock()
    mock_cred_manager.get_access_token.side_effect = [
        mock_access_token_value1,
        mock_access_token_value2,
    ]

    url = "https://fhir-url"

    initial_access_token = mock_cred_manager.get_access_token()
    response = http_request_with_reauth(
        cred_manager=mock_cred_manager,
        url=url,
        retry_count=3,
        request_type="GET",
        allowed_methods=["GET"],
        headers={"Authorization": f"Bearer {initial_access_token}"},
    )

    assert response.status_code == 401

    mock_cred_manager.get_access_token.call_count == 2

    mock_requests_session_instance.get.assert_called_with(
        url=url, headers={"Authorization": f"Bearer {mock_access_token_value2}"}
    )
    mock_requests_session_instance.get.call_count == 2


@mock.patch("requests.Session")
def test_export_from_fhir_server(mock_requests_session):
    mock_requests_session_instance = mock_requests_session.return_value

    mock_access_token_value = "some-token"
    mock_cred_manager = mock.Mock()
    mock_cred_manager.get_access_token.return_value = mock_access_token_value

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
    mock_cred_manager = mock.Mock()
    mock_cred_manager.get_access_token.return_value = mock_access_token_value

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
    mock_cred_manager = mock.Mock()
    mock_cred_manager.get_access_token.return_value = mock_access_token_value

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
