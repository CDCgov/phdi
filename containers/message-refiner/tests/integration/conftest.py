import os
from pathlib import Path

import pytest
from testcontainers.compose import DockerCompose


@pytest.fixture(scope="session")
def setup(request):
    print("Setting up tests...")
    path = Path(__file__).resolve().parent.parent.parent
    compose_file_name = os.path.join(path, "docker-compose.yml")
    orchestration_service = DockerCompose(path, compose_file_name=compose_file_name)

    orchestration_service.start()

    port_number_dict = {
        "MESSAGE_REFINER_PORT_NUMBER": "8080",
        "TRIGGER_CODE_REFERENCE_PORT_NUMBER": "8081",
    }
    for name, port in port_number_dict.items():
        print(name, "loading...")
        orchestration_service.wait_for(f"http://0.0.0.0:{port}")
        print(name, "started!")

    print("Message refiner services ready to test!")

    def teardown():
        print("Tests finished! Tearing down.")

    request.addfinalizer(teardown)
