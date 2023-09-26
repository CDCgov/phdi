import pytest
import os
from testcontainers.compose import DockerCompose


@pytest.fixture(scope="session")
def setup(request):
    print("Setting up tests...")
    compose_path = os.path.join(os.path.dirname(__file__), "./")
    compose_file_name = "docker-compose.yaml"
    # compose_validation_file_name = "docker-compose-validation.yaml"
    orchestration_service = DockerCompose(
        compose_path, compose_file_name=compose_file_name
    )
    # validation_service = DockerCompose(
    #     compose_path, compose_file_name=compose_validation_file_name
    # )

    orchestration_url = "http://0.0.0.0:8080"
    # validation_url = "http://0.0.0.0:8081"

    # validation_service.start()
    orchestration_service.start()
    # validation_service.wait_for(validation_url)
    orchestration_service.wait_for(orchestration_url)
    print("Orchestration etc. services ready to test!")

    def teardown():
        print("\nContainer output: ")
        print(orchestration_service.get_logs())
        print("Tests finished! Tearing down.")
        orchestration_service.stop()
        # validation_service.stop()

    request.addfinalizer(teardown)
