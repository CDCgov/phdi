import os
import pytest
from unittest import mock

from Import.main import unzip_input_file
from Import.main import process_ndjson_files
from Import.main import read_file
from Import.main import get_access_token


# This fixture runs before all tests and can be passed as arguments to individual
# tests to enable accessing the variables they define.
# More info: https://docs.pytest.org/en/latest/fixture.html#fixtures-scope-sharing-and-autouse-autouse-fixtures  # noqa: E501
# @pytest.fixture(scope="session", autouse=True)

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
    unzip_input_file("./assets/test_files.zip")
    assert os.path.isfile("./FhirResources/test_files/Claim-1.ndjson")
    assert os.path.isfile("./FhirResources/test_files/Organization-1.ndjson")
