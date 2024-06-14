import json
import os
from pathlib import Path

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_list_loaded_configs():
    response = client.get("/configs")
    default_configs = os.listdir(
        Path(__file__).parent.parent / "app" / "default_configs"
    )
    assert response.status_code == 200
    assert response.json()["default_configs"] == default_configs


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
        "workflow": test_config,
    }


def test_config_not_found():
    response = client.get("/configs/some-config-that-does-not-exist.json")
    assert response.status_code == 400
    assert response.json() == {
        "message": "A config with the name 'some-config-that-does-not-exist.json' "
        + "could not be found.",
        "workflow": {},
    }


def test_upload_config():
    request_body = {
        "workflow": {
            "workflow": [
                {
                    "service": "ingestion",
                    "url": "some-url-for-an-ingestion-service",
                    "endpoint": "/fhir/harmonization/standardization/standardize_names",
                }
            ]
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

    # Attempt to upload a config with name that already exists.
    response = client.put(
        "/configs/test_config1.json",
        json=request_body,
    )
    assert response.status_code == 400
    assert response.json() == {
        "message": f"A config for the name '{test_config_name}' already exists. "
        "To proceed submit a new request with a different config name or set the "
        "'overwrite' field to 'true'."
    }

    # Upload a config with name that already exists and overwrite it.
    request_body["overwrite"] = True
    response = client.put(
        "/configs/test_config1.json",
        json=request_body,
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Config updated successfully!"}

    # Delete the test config to avoid conflicts with other tests.
    processing_config = (
        Path(__file__).parent.parent / "app" / "custom_configs" / test_config_name
    )
    processing_config.unlink()
