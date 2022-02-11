import json
import os
from importlib.resources import files
from pathlib import Path


# def pytest_generate_tests(metafunc):
#     local_settings_path = Path(metafunc.module.__file__).parent / "assets" / "test.settings.json"
#     local_json_config = json.loads(local_settings_path.read_text())
#     local_settings_vals = local_json_config.get("Values")
#     os.environ["PrivateKeyPassword"] = local_settings_vals.get("PrivateKeyPassword")
#     os.environ["PrivateKey"] = local_settings_vals.get("PrivateKey")
