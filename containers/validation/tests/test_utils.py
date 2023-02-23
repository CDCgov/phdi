import pathlib
from app.utils import load_config, validate_error_types

config_path = pathlib.Path(__file__).parent.parent / "config" / "sample_ecr_config.yaml"


def test_load_config():
    print("HERE:")
    print(config_path)
    config = load_config(config_path)
    assert config != ""


def test_validate_error_types():
    valid_ets = "error,warn"
    invalid_ets = "blah,info"
    invalid_ets2 = "blah, nope, wrong"
    invalid_ets3 = "info,blah, nope, wrong,warn"
    null_ets = ""

    assert validate_error_types(valid_ets) == valid_ets
    assert validate_error_types(invalid_ets) == "info"
    assert validate_error_types(invalid_ets2) == ""
    assert validate_error_types(invalid_ets3) == "info,warn"
    assert validate_error_types(null_ets) == ""
    assert validate_error_types(None) == ""
