import json
from pathlib import Path
import pytest
from app.utils import (
    load_processing_config
)


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
    assert error.value.args == (
        f"A config with the name '{bad_config_name}' could not be found.",
    )

