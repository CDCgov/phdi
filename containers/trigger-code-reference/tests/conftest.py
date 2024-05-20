import json
import os
from pathlib import Path

import pytest
from testcontainers.compose import DockerCompose


@pytest.fixture(scope="session")
def read_json_from_test_assets():
    def _read_json(filename: str) -> dict:
        """
        Reads a JSON file from the test assets directory.
        """
        with open((Path(__file__).parent / "assets" / filename), "r") as file:
            return json.load(file)

    return _read_json


@pytest.fixture(scope="session")
def setup(request):
    print("Setting up tests...")
    compose_path = os.path.join(os.path.dirname(__file__), "./integration/")
    compose_file_name = "docker-compose.yaml"
    trigger_code_reference = DockerCompose(
        compose_path, compose_file_name=compose_file_name
    )
    parser_url = "http://0.0.0.0:8080"

    trigger_code_reference.start()
    trigger_code_reference.wait_for(parser_url)
    print("Trigger Code Reference ready to test!")

    def teardown():
        print("Service logs...\n")
        print(trigger_code_reference.get_logs())
        print("Tests finished! Tearing down.")
        trigger_code_reference.stop()

    request.addfinalizer(teardown)
