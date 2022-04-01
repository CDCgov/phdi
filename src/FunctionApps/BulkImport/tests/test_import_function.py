import os
from unittest import mock
from pathlib import Path

from Import.main import unzip_input_file
from Import.main import get_access_token

TEST_ENV = {
    "TENANT_ID": "a-tenant-id",
    "CLIENT_ID": "a-client-id",
    "CLIENT_SECRET": "a-client-secret",
    "FHIR_URL": "https://some-fhir-server",
}


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


def test_file_unzip():
    test_file_path = Path("BulkImport").parent / "tests" / "assets" / "test_files.zip"
    unzip_input_file(test_file_path)
    assert os.path.isfile("./FhirResources/test_files/Claim-1.ndjson")
    assert os.path.isfile("./FhirResources/test_files/Organization-1.ndjson")
