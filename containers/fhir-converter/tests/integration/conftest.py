import pytest
import os
from testcontainers.compose import DockerCompose


@pytest.fixture(scope="session")
def setup(request):
    print("Setting up tests...")
    compose_path = os.path.join(os.path.dirname(__file__), "./")
    compose_file_name = "docker-compose.yaml"
    fhir_converter = DockerCompose(compose_path, compose_file_name=compose_file_name)
    converter_url = "http://0.0.0.0:8080"

    fhir_converter.start()
    fhir_converter.wait_for(converter_url)
    print("FHIR Converter ready to test!")

    def teardown():
        print("Tests finished! Tearing down.")
        fhir_converter.stop()

    request.addfinalizer(teardown)
