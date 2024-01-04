import json
from pathlib import Path
import pytest
from app.utils import load_processing_config, search_for_ecr_data
from zipfile import ZipFile


def test_load_processing_config_success():
    test_config_path = (
        Path(__file__).parent.parent / "app" / "default_configs" / "test_config.json"
    )
    with open(test_config_path, "r") as file:
        test_config = json.load(file)

    config = load_processing_config("test_config.json")
    assert config == test_config


def test_load_processing_config_fail():
    bad_config_name = "config-that-does-not-exist.json"
    with pytest.raises(FileNotFoundError) as error:
        load_processing_config(bad_config_name)
    response = error.value.args
    assert response == (
        f"A config with the name '{bad_config_name}' could not be found.",
    )


def test_search_for_ecr_data_with_eicr_present_success():
    valid_zipfile = ZipFile(
        Path(__file__).parent.parent.parent.parent
        / "tests"
        / "assets"
        / "orchestration"
        / "test_zip.zip"
    )

    response = search_for_ecr_data(valid_zipfile)
    assert response["ecr"] is not None
    assert response.get("rr") is None


def test_search_for_ecr_data_with_eicr_rr_present_success():
    valid_zipfile = ZipFile(
        Path(__file__).parent.parent.parent.parent
        / "tests"
        / "assets"
        / "orchestration"
        / "eICR_RR_combo.zip"
    )

    response = search_for_ecr_data(valid_zipfile)
    assert response["ecr"] is not None
    assert response.get("rr") is not None


def test_search_for_ecr_data_eicr_not_found_fails():
    zipfile_without_eicr = ZipFile(
        Path(__file__).parent.parent.parent.parent
        / "tests"
        / "assets"
        / "orchestration"
        / "no_eicr.zip"
    )

    with pytest.raises(IndexError) as indexError:
        search_for_ecr_data(zipfile_without_eicr)
    error_message = str(indexError.value)
    assert "There is no eICR in this zip file." in error_message
