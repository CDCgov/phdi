from pathlib import Path
import json
from fastapi.testclient import TestClient
from app.main import app
import os


client = TestClient(app)


def test_list_loaded_configs():
    response = client.get("/configs")
    default_configs = os.listdir(
        Path(__file__).parent.parent / "app" / "default_configs"
    )
    assert response.status_code == 200
    assert response.json() == {
        "default_configs": default_configs,
        "custom_configs": [],
    }


def test_get_specific_config():
    test_config_path = (
        Path(__file__).parent.parent / "app" / "default_configs" / "test_config.json"
    )
    with open(test_config_path, "r") as file:
        test_config = json.load(file)

    response = client.get("/configs/test_config.json")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Config found!",
        "processing_config": test_config,
    }


def test_config_not_found():
    response = client.get("/configs/some-config-that-does-not-exist.json")
    assert response.status_code == 400
    print(
        str(
            {
                "message": "A config with the name 'some-config-that-does-not-exist.json' "
                "could not be found.",
                "processing_config": {},
            }
        )
    )
    assert response.json() == {
        "message": "A config with the name 'some-config-that-does-not-exist.json' "
        + "could not be found.",
        "processing_config": {},
    }


def test_upload_config():
    request_body = {
        "processing_config": {
            "my_field": {
                "fhir_path": "some-path",
                "data_type": "string",
                "nullable": True,
                "secondary_config": {
                    "my_sub_field": {
                        "fhir_path": "some-path",
                        "data_type": "string",
                        "nullable": True,
                    }
                },
            }
        }
    }
    test_config_name = "test_config1.json"

    # Upload a new config.
    response = client.put(
        f"/configs/{test_config_name}",
        json=request_body,
    )
    assert response.status_code == 201
    assert response.json() == {"message": "Config uploaded successfully!"}

    response = client.put(
        "/configs/test_config1.json",
        json=request_body,
    )

    # Attempt to upload a config with name that already exists.
    assert response.status_code == 400
    assert response.json() == {
        "message": f"A config for the name '{test_config_name}' already exists. "
        "To proceed submit a new request with a different config name or set the "
        "'overwrite' field to 'true'."
    }
    request_body["overwrite"] = True
    response = client.put(
        "/configs/test_config1.json",
        json=request_body,
    )

    # Upload a config with name that already exists and overwrite it.
    assert response.status_code == 200
    assert response.json() == {"message": "Config updated successfully!"}

    # Delete the test config to avoid conflicts with other tests.
    processing_config = (
        Path(__file__).parent.parent / "app" / "custom_configs" / test_config_name
    )
    processing_config.unlink()
