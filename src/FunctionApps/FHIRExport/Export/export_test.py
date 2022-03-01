from Export import main
from Export import get_access_token
from Export import poll
from Export import POLLING_FREQUENCY

import pytest
from unittest import mock

import azure.functions as func


TEST_ENV = {
    "TENANT_ID": "a-tenant-id",
    "CLIENT_ID": "a-client-id",
    "CLIENT_SECRET": "a-client-secret",
    "FHIR_URL": "https://some-fhir-server",
}


@mock.patch("requests.get")
@mock.patch("Export.poll")
@mock.patch("Export.get_access_token")
@mock.patch.dict("os.environ", TEST_ENV)
def test_main(mock_token, mock_poll, mock_get):
    mock_token.return_value = "some-access-token"

    # The export endpoint returns a 202 if it started the export
    mock_get.return_value = mock.Mock(status_code=202)

    # The polling endpoint should eventually return a 200
    mock_poll.return_value = mock.Mock(status_code=200, text="{}")

    resp = main(func.HttpRequest(method="GET", url="/", body="", params={}))
    assert resp.status_code == 200

    mock_token.assert_called()
    mock_get.assert_called_with(
        "https://some-fhir-server/$export",
        headers={
            "Authorization": "Bearer some-access-token",
            "Accept": "application/fhir+json",
            "Prefer": "respond-async",
        },
    )


@mock.patch("requests.get")
def test_poll_success(mock_get):
    """Check what happens when the requests succeeds the first time"""
    mock_get.return_value = mock.Mock(status_code=200, text="{}")

    resp = poll("some-endpoint", "some-token")
    assert 200 == resp.status_code
    assert "{}" == resp.text

    mock_get.assert_called_with(
        "some-endpoint", headers={"Authorization": "Bearer some-token"}
    )


@mock.patch("requests.get")
def test_poll_failure(mock_get):
    """
    The first time we check status requests.get will return a 500, at which
    point we'd assume the export errored out (so we should too)
    """

    mock_get.return_value = mock.Mock(ok=False, status_code=500, text="kablamo")
    with pytest.raises(Exception):
        poll("some-endpoint", "some-token")


@mock.patch("requests.get")
@mock.patch("time.sleep")
def test_poll_eventual_success(mock_sleep, mock_get):
    """Status endpoint polls twice and then succeeds"""
    mock_get.side_effect = [
        mock.Mock(status_code=202),
        mock.Mock(status_code=202),
        mock.Mock(status_code=200, text="{}"),
    ]

    resp = poll("some-endpoint", "some-token")
    assert 200 == resp.status_code
    assert "{}" == resp.text

    mock_sleep.assert_called_with(POLLING_FREQUENCY)


@mock.patch("requests.get")
@mock.patch("time.sleep")
def test_poll_timeout(mock_sleep, mock_get):
    """
    every time requests.get is called, it'll return a
    202 ('Accepted' or in progress) until we're out of remaining retries
    """

    mock_get.return_value = mock.Mock(status_code=202)
    with pytest.raises(Exception):
        poll("some-endpoint", "some-token")


@mock.patch("requests.post")
@mock.patch.dict("os.environ", TEST_ENV)
def test_get_access_token(mock_post):
    resp = mock.Mock()
    resp.json.return_value = {"access_token": "some-access-token"}
    mock_post.return_value = resp

    assert "some-access-token" == get_access_token()

    mock_post.assert_called_with(
        "https://login.microsoftonline.com/a-tenant-id/oauth2/token",
        data={
            "grant_type": "client_credentials",
            "client_id": "a-client-id",
            "client_secret": "a-client-secret",
            "resource": "https://some-fhir-server",
        },
    )


@mock.patch("requests.post")
def test_get_access_token_exception(mock_post):
    mock_post.return_value = mock.Mock(ok=False)
    with pytest.raises(Exception):
        get_access_token()
