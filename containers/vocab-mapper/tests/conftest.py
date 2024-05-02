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
def read_json_from_phdi_test_assets():
    def _read_json(filename: str) -> dict:
        """
        Reads a JSON file from the test assets directory.
        """
        with open(
            (
                Path(__file__).parent.parent.parent.parent
                / "tests"
                / "assets"
                / "general"
                / filename
            ),
            "r",
        ) as file:
            return json.load(file)

    return _read_json


@pytest.fixture(scope="session")
def read_file_from_test_assets():
    def _read_file(filename: str) -> str:
        """
        Reads a file from the test assets directory.
        """
        with open((Path(__file__).parent / "assets" / filename), "r") as file:
            return file.read()

    return _read_file


@pytest.fixture(scope="session")
def setup(request):
    print("Setting up tests...")
    compose_path = os.path.join(os.path.dirname(__file__), "./integration/")
    compose_file_name = "docker-compose.yaml"
    vocab_mapper = DockerCompose(compose_path, compose_file_name=compose_file_name)
    parser_url = "http://0.0.0.0:8080"

    vocab_mapper.start()
    vocab_mapper.wait_for(parser_url)
    print("Vocabulary Mapper ready to test!")

    def teardown():
        print("Service logs...\n")
        print(vocab_mapper.get_logs())
        print("Tests finished! Tearing down.")
        vocab_mapper.stop()

    request.addfinalizer(teardown)
