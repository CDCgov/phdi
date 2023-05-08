from phdi.containers.base_service import LicenseType, BaseService
from fastapi.testclient import TestClient
from pathlib import Path
from importlib import metadata

default_app_version = metadata.version("phdi")
default_app_contact = BaseService.DIBBS_CONTACT
default_app_license = LicenseType.CreativeCommonsZero
alternate_app_license = LicenseType.MIT


def test_base_service():
    service = BaseService(
        service_name="test_service",
        description_path=Path(__file__).parent.parent
        / "assets"
        / "test_description.md",
    )
    assert service.app.title == "test_service"
    assert service.app.version == default_app_version
    assert service.app.contact == default_app_contact
    assert service.app.license_info == default_app_license
    assert service.app.description == "This is a test description."

    client = TestClient(service.start())
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}


def test_base_service_alternate_license():
    service = BaseService(
        service_name="test_service",
        description_path=Path(__file__).parent.parent
        / "assets"
        / "test_description.md",
        license_info=alternate_app_license,
    )
    assert service.app.title == "test_service"
    assert service.app.version == default_app_version
    assert service.app.contact == default_app_contact
    assert service.app.license_info == alternate_app_license
    assert service.app.description == "This is a test description."
