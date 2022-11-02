import os
from pydantic import ValidationError
import pytest
from app.config import get_settings


def test_get_settings_success():
    os.environ["CRED_MANAGER"] = "azure"
    os.environ["FHIR_URL"] = "some-FHIR-server-URL"
    os.environ["SALT_STR"] = "my-salt"
    os.environ["AUTH_ID"] = "test_id"
    os.environ["AUTH_TOKEN"] = "test_token"
    os.environ["CLOUD_PROVIDER"] = "azure"
    os.environ["BUCKET_NAME"] = "my_bucket"
    os.environ["STORAGE_ACCOUNT_URL"] = "storage_url"
    get_settings.cache_clear()
    assert get_settings() == {
        "cred_manager": "azure",
        "fhir_url": "some-FHIR-server-URL",
        "salt_str": "my-salt",
        "auth_id": "test_id",
        "auth_token": "test_token",
        "cloud_provider": "azure",
        "bucket_name": "my_bucket",
        "storage_account_url": "storage_url",
    }
    os.environ.pop("CRED_MANAGER", None)
    os.environ.pop("CLOUD_PROVIDER", None)
    os.environ.pop("AUTH_ID", None)
    os.environ.pop("AUTH_TOKEN", None)
    os.environ.pop("BUCKET_NAME", None)
    os.environ.pop("STORAGE_ACCOUNT_URL", None)


def test_get_settings_failure_creds():
    os.environ["CRED_MANAGER"] = "some-unknown-cred-manager"
    get_settings.cache_clear()

    with pytest.raises(ValidationError):
        get_settings()
    os.environ.pop("CRED_MANAGER", None)


def test_get_settings_failure_cloud():
    os.environ["CLOUD_PROVIDER"] = "some-unknown-cloud"
    get_settings.cache_clear()

    with pytest.raises(ValidationError):
        get_settings()
    os.environ.pop("CLOUD_PROVIDER", None)
