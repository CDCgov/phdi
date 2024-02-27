import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from testcontainers.compose import DockerCompose


@pytest.fixture(scope="session")
def setup(request):
    print("Setting up tests...")
    path = Path(__file__).resolve().parent.parent.parent
    load_dotenv(dotenv_path=os.path.join(path, ".env"))
    compose_file_name = os.path.join(path, "docker-compose.yml")
    orchestration_service = DockerCompose(path, compose_file_name=compose_file_name)

    orchestration_service.start()

    port_number_strings = [
        "ORCHESTRATION_PORT_NUMBER",
        "VALIDATION_PORT_NUMBER",
        "FHIR_CONVERTER_PORT_NUMBER",
        "INGESTION_PORT_NUMBER",
        "MESSAGE_PARSER_PORT_NUMBER",
    ]
    for port_number in port_number_strings:
        port = os.getenv(port_number)
        orchestration_service.wait_for(f"http://0.0.0.0:{port}")

    print("Orchestration etc. services ready to test!")

    def teardown():
        print("Tests finished! Tearing down.")
        # orchestration_service.stop()

    request.addfinalizer(teardown)
