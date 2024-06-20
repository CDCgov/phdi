import json
import os
from pathlib import Path
from unittest.mock import Mock
from zipfile import ZipFile

import pytest
from app.utils import _combine_response_bundles
from app.utils import load_processing_config
from app.utils import replace_env_var_placeholders
from app.utils import search_for_ecr_data
from fastapi import Response


def test_load_processing_config_success():
    test_config_path = (
        Path(__file__).parent.parent / "app" / "default_configs" / "test_config.json"
    )
    with open(test_config_path, "r") as file:
        test_config = json.load(file)

    config = load_processing_config("test_config.json")
    assert config == test_config


def test_replace_env_var_placeholders():
    # Setup a test config with known placeholders
    test_config = {
        "configurations": {
            "service1": {"url": "${TEST_SERVICE_URL}"},
            "service2": {"url": "http://fixedurl.com"},
        }
    }

    # Set up the environment variables to match
    os.environ["TEST_SERVICE_URL"] = "http://testservice.com"

    # Call the function to replace placeholders
    replace_env_var_placeholders(test_config)

    # Assert the placeholders were replaced correctly
    assert test_config["configurations"]["service1"]["url"] == "http://testservice.com"
    assert test_config["configurations"]["service2"]["url"] == "http://fixedurl.com"


def test_load_processing_config_fail():
    bad_config_name = "config-that-does-not-exist.json"
    with pytest.raises(FileNotFoundError) as error:
        load_processing_config(bad_config_name)
    response = error.value.args
    assert response == (
        f"A config with the name '{bad_config_name}' could not be found.",
    )


def test_search_for_ecr_data_with_eicr_present_success():
    valid_zipfile = ZipFile(Path(__file__).parent / "assets" / "test_zip.zip")

    response = search_for_ecr_data(valid_zipfile)
    assert response["ecr"] is not None
    assert response.get("rr") is None


def test_search_for_ecr_data_with_eicr_rr_present_success():
    valid_zipfile = ZipFile(Path(__file__).parent / "assets" / "eICR_RR_combo.zip")

    response = search_for_ecr_data(valid_zipfile)
    assert response["ecr"] is not None
    assert response.get("rr") is not None


def test_search_for_ecr_data_eicr_not_found_fails():
    zipfile_without_eicr = ZipFile(Path(__file__).parent / "assets" / "no_eicr.zip")

    with pytest.raises(IndexError) as indexError:
        search_for_ecr_data(zipfile_without_eicr)
    error_message = str(indexError.value)
    assert "There is no eICR in this zip file." in error_message


def test_combine_response_bundles():
    mock_response = Mock(spec=Response)
    mock_response.status_code = 200
    mock_response.json = Mock(return_value={"foo": "bar"})

    mock_response_2 = Mock(spec=Response)
    mock_response_2.status_code = 200
    mock_response_2.json = Mock(return_value={"biz": "boo"})

    config = {"workflow": [{"service": "foobar"}], "include": ["foo", "biz"]}

    combined = _combine_response_bundles(
        mock_response, {"foobar": mock_response_2}, config
    )

    assert "foo" in combined
    assert "biz" in combined
