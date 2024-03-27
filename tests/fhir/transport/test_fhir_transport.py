import json
import pathlib
import re
from unittest import mock

import polling
import pytest
import requests

from phdi.fhir.transport import export_from_fhir_server
from phdi.fhir.transport import http_request_with_reauth
from phdi.fhir.transport.export import _compose_export_url
from phdi.fhir.transport.http import _log_fhir_server_error
from phdi.fhir.transport.http import _split_bundle_resources
from phdi.fhir.transport.http import fhir_server_get
from phdi.fhir.transport.http import upload_bundle_to_fhir_server


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


@mock.patch("phdi.fhir.transport.http.http_request_with_reauth")
def test_upload_bundle_to_fhir_server(patch_http_request):
    bundle = {
        "resourceType": "Bundle",
        "entry": [{"resource": {"resourceType": "Patient"}}],
    }

    mock_response = {
        "resourceType": "Bundle",
        "entry": [
            {"resource": {"resourceType": "Patient"}, "response": {"status": "200"}}
        ],
    }

    fhir_url = "https://some-fhir-url"

    patch_http_request.return_value = mock.Mock(
        status_code=200, json=(lambda: mock_response)
    )

    cred_manager = mock.Mock(get_access_token=(lambda: "some-token"))

    response = upload_bundle_to_fhir_server(
        bundle=bundle, cred_manager=cred_manager, fhir_url=fhir_url
    )

    assert response[0].status_code == 200
    assert response[0].json() == mock_response


@mock.patch("phdi.fhir.transport.http.http_request_with_reauth")
@mock.patch("phdi.fhir.transport.http._log_fhir_server_error")
def test_upload_bundle_to_fhir_server_failure(patch_log_error, patch_http_request):
    bundle = {
        "resourceType": "Bundle",
        "entry": [{"resource": {"resourceType": "Patient"}}],
    }

    fhir_url = "https://some-fhir-url"

    patch_http_request.return_value = mock.Mock(status_code=400)

    cred_manager = mock.Mock(get_access_token=(lambda: "some-token"))

    response = upload_bundle_to_fhir_server(
        bundle=bundle, cred_manager=cred_manager, fhir_url=fhir_url
    )

    assert response[0].status_code == 400

    patch_log_error.assert_called_with(400)


@mock.patch("phdi.fhir.transport.http.http_request_with_reauth")
@mock.patch("phdi.fhir.transport.http._log_fhir_server_error")
def test_upload_bundle_to_fhir_server_embedded_failure(
    patch_log_error, patch_http_request
):
    bundle = {
        "resourceType": "Bundle",
        "entry": [{"resource": {"resourceType": "Patient"}}],
    }

    mock_response = {
        "resourceType": "Bundle",
        "entry": [
            {"resource": {"resourceType": "Patient"}, "response": {"status": "400"}}
        ],
    }

    fhir_url = "https://some-fhir-url"

    patch_http_request.return_value = mock.Mock(
        status_code=200, json=(lambda: mock_response)
    )

    cred_manager = mock.Mock(get_access_token=(lambda: "some-token"))

    response = upload_bundle_to_fhir_server(
        bundle=bundle, cred_manager=cred_manager, fhir_url=fhir_url
    )

    assert response[0].status_code == 200
    assert response[0].json() == mock_response

    patch_log_error.assert_called_with(status_code=400, batch_entry_index=0)


@mock.patch("phdi.fhir.transport.http.http_request_with_reauth")
def test_fhir_server_get(patch_http_request):
    fhir_url = "https://some-fhir-url/Patient/1"
    access_token = "some-token"

    mock_response = {"resourceType": "Patient", "id": 1}

    patch_http_request.return_value = mock.Mock(
        status_code=200, json=(lambda: mock_response)
    )

    cred_manager = mock.Mock(get_access_token=(lambda: access_token))

    response = fhir_server_get(url=fhir_url, cred_manager=cred_manager)

    assert response.status_code == 200
    assert response.json() == mock_response


@mock.patch("logging.error")
def test_log_fhir_server_error(patch_log_error):
    _log_fhir_server_error(200)
    patch_log_error.assert_not_called()

    _log_fhir_server_error(400)
    assert re.fullmatch("^FHIR SERVER ERROR -.*400$", patch_log_error.call_args.args[0])

    _log_fhir_server_error(401)
    assert re.fullmatch(
        "^FHIR SERVER ERROR -.*401:.*$", patch_log_error.call_args.args[0]
    )

    _log_fhir_server_error(403)
    assert re.fullmatch(
        "^FHIR SERVER ERROR -.*403:.*$", patch_log_error.call_args.args[0]
    )

    _log_fhir_server_error(404)
    assert re.fullmatch(
        "^FHIR SERVER ERROR -.*404:.*$", patch_log_error.call_args.args[0]
    )

    _log_fhir_server_error(410)
    assert re.fullmatch(
        "^FHIR SERVER ERROR -.*410:.*$", patch_log_error.call_args.args[0]
    )

    _log_fhir_server_error(410, 0)
    assert re.fullmatch(
        "^FHIR SERVER ERROR in zero-based message index 0 of FHIR batch -.*410:.*$",
        patch_log_error.call_args.args[0],
    )


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
def test_export_from_fhir_server_failure(mock_requests_session):
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

    mock_export_download_response_failed = mock.Mock()
    mock_export_download_response_failed.status_code = 400

    mock_requests_session_instance.get.side_effect = [
        mock_export_response,
        mock_export_download_response_failed,
    ]

    with pytest.raises(requests.HTTPError):
        export_from_fhir_server(
            cred_manager=mock_cred_manager,
            fhir_url=fhir_url,
            poll_step=poll_step,
            poll_timeout=poll_timeout,
        )

    assert mock_requests_session_instance.get.call_count == 2


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


def test_split_bundle_resources():
    bundle = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "general"
            / "patient_bundle.json"
        )
    )

    my_count = len(_split_bundle_resources(bundle=bundle)[0].get("entry"))
    assert my_count == 2

    bundle = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "fhir-converter"
            / "ecr"
            / "example_eicr_with_rr_data_with_person.json"
        )
    )

    my_count = len(_split_bundle_resources(bundle=bundle)[0].get("entry"))
    assert my_count == 53

    single_resource = bundle.get("entry")[0]
    # add 500 resources to bundle and then pass to function
    for x in range(500):
        bundle["entry"].append(single_resource)

    my_count = len(bundle.get("entry"))
    assert my_count == 553

    split_bundles = _split_bundle_resources(bundle=bundle)
    assert len(split_bundles) == 2

    assert len(split_bundles[0].get("entry")) == 500
    assert len(split_bundles[1].get("entry")) == 53

    # add an additional 500 resources to bundle and then pass to function
    for x in range(500):
        bundle["entry"].append(single_resource)

    my_count = len(bundle.get("entry"))
    assert my_count == 1053

    split_bundles = _split_bundle_resources(bundle=bundle)
    assert len(split_bundles) == 3

    assert len(split_bundles[0].get("entry")) == 500
    assert len(split_bundles[1].get("entry")) == 500
    assert len(split_bundles[2].get("entry")) == 53

    bundle["entry"] = []
    split_bundles = _split_bundle_resources(bundle=bundle)
    assert len(split_bundles) == 1
    assert len(split_bundles[0].get("entry")) == 0
