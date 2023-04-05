from phdi.containers.base_service import BaseService
from fastapi.testclient import TestClient
from pathlib import Path


def test_base_service():
    service = BaseService(
        "test_service", Path(__file__).parent.parent / "assets" / "test_description.md"
    )
    assert service.app.title == "test_service"
    assert service.app.version == "0.0.1"
    assert service.app.contact == {
        "name": "CDC Public Health Data Infrastructure",
        "url": "https://cdcgov.github.io/phdi-site/",
        "email": "dmibuildingblocks@cdc.gov",
    }
    assert service.app.license_info == {
        "name": "Creative Commons Zero v1.0 Universal",
        "url": "https://creativecommons.org/publicdomain/zero/1.0/",
    }
    assert service.app.description == "This is a test description."

    client = TestClient(service.start())
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}
