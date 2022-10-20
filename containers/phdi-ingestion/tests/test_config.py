import os

from pydantic import ValidationError
import pytest
from app.config import get_settings


def test_get_settings_success():
    os.environ["CREDENTIAL_MANAGER"] = "azure"
    os.environ["FHIR_URL"] = "some-FHIR-server-URL"
    os.environ["SALT_STR"] = "my-salt"
    get_settings.cache_clear()
    assert get_settings() == {
        "credential_manager": "azure",
        "fhir_url": "some-FHIR-server-URL",
        "salt_str": "my-salt",
    }


def test_get_settings_failure():
    os.environ["CREDENTIAL_MANAGER"] = "some-unknown-cred-manager"

    get_settings.cache_clear()
    with pytest.raises(ValidationError):
        get_settings()
