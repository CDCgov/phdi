import os

from pydantic import ValidationError
import pytest
from app.config import get_settings


def test_get_settings_success():
    os.environ["CREDENTIAL_MANAGER"] = "azure"
    os.environ["FHIR_URL"] = "some-FHIR-server-URL"
    os.environ["SALT_STR"] = "my-salt"
    os.environ["AUTH_ID"] = "test_id"
    os.environ["AUTH_TOKEN"] = "test_token"
    get_settings.cache_clear()
    assert get_settings() == {
        "credential_manager": "azure",
        "fhir_url": "some-FHIR-server-URL",
        "salt_str": "my-salt",
        "auth_id": "test_id",
        "auth_token": "test_token"
    }
    os.environ.pop("CREDENTIAL_MANAGER",None)



def test_get_settings_failure():
    os.environ["CREDENTIAL_MANAGER"] = "some-unknown-cred-manager"

    get_settings.cache_clear()
    with pytest.raises(ValidationError):
        get_settings()
    os.environ.pop("CREDENTIAL_MANAGER",None)
    os.environ.pop("AUTH_ID",None)
    os.environ.pop("AUTH_TOKEN",None)
    os.environ.pop("FHIR_URL",None)
    os.environ.pop("SALT_STR",None)
