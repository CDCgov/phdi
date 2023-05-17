from phdi.containers.base_service import LICENSES, DIBBS_CONTACT, BaseService
from fastapi.testclient import TestClient
from pathlib import Path
from importlib import metadata

default_app_version = metadata.version("phdi")


def test_base_service():
    service = BaseService(
        "test_service",
        Path(__file__).parent.parent / "assets" / "containers" / "test_description.md",
    )
    assert service.app.title == "test_service"
    assert service.app.version == default_app_version
    assert service.app.contact == DIBBS_CONTACT
    assert service.app.license_info == LICENSES["CreativeCommonsZero"]
    assert service.app.description == "This is a test description."

    client = TestClient(service.start())
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}

    response = client.get("/redoc")
    assert response.status_code == 200


def test_base_service_alternate_license():
    service = BaseService(
        service_name="test_service",
        description_path=Path(__file__).parent.parent
        / "assets"
        / "containers"
        / "test_description.md",
        license_info="MIT",
    )
    assert service.app.title == "test_service"
    assert service.app.version == default_app_version
    assert service.app.contact == DIBBS_CONTACT
    assert service.app.license_info == LICENSES["MIT"]
    assert service.app.description == "This is a test description."

    client = TestClient(service.start())
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}

    response = client.get("/redoc")
    assert response.status_code == 200
