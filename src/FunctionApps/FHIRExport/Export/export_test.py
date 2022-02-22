from Export import main
from Export import get_access_token

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
@mock.patch("Export.get_access_token")
@mock.patch.dict("os.environ", TEST_ENV)
def test_main(mock_token, mock_get):
    mock_token.return_value = "some-access-token"

    # The export endpoint returns a 202 if it started the export
    mock_resp = mock.Mock()
    mock_resp.status_code = 202
    mock_get.return_value = mock_resp

    resp = main(func.HttpRequest(method="GET", url="/", body="", params={}))
    assert resp.status_code == 202

    mock_token.assert_called()
    mock_get.assert_called_with(
        "https://some-fhir-server/$export",
        headers={
            "Authorization": "Bearer some-access-token",
            "Accept": "application/fhir+json",
            "Prefer": "respond-async",
        },
    )


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
    resp = mock.Mock()
    resp.status_code = 401

    with pytest.raises(Exception):
        get_access_token()
