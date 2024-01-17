import os

import pytest
from testcontainers.compose import DockerCompose


@pytest.fixture(scope="session")
def setup(request):
    print("Setting up tests...")
    compose_path = os.path.join(os.path.dirname(__file__), "./")
    compose_file_name = "docker-compose.yaml"
    message_parser = DockerCompose(
        compose_path, compose_file_name=compose_file_name, build=True
    )
    parser_url = "http://0.0.0.0:8080"

    message_parser.start()
    message_parser.wait_for(parser_url)
    print("Message Parser ready to test!")

    def teardown():
        print("Service logs...\n")
        print(message_parser.get_logs())
        print("Tests finished! Tearing down.")
        message_parser.stop()

    request.addfinalizer(teardown)
