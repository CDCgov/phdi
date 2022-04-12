import pytest

from unittest import mock

from config import get_required_config


@mock.patch.dict("os.environ", {"INTAKE_CONTAINER_PREFIX": "some-prefix"})
def test_get_required_config():
    assert get_required_config("INTAKE_CONTAINER_PREFIX") == "some-prefix"
    with pytest.raises(Exception):
        # Make sure we raise an exception if some config is missing
        assert get_required_config("INTAKE_CONTAINER_SUFFIX")
