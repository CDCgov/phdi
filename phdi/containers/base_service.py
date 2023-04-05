from fastapi import FastAPI
from pathlib import Path


class BaseService:
    """
    Base class for all DIBBs services. This class provides a FastAPI instance with DIBBs
    metadata and optionally a health check endpoint.
    """

    def __init__(
        self,
        service_name: str,
        description_path: str,
        include_health_check_endpoint: bool = True,
    ):
        """
        Initialize a BaseService instance.

        :param service_name: The name of the service.
        :param description_path: The path to a markdown file containing a description of
            the service.
        :param include_health_check_endpoint: If True, the standard DIBBs health check
            endpoint will be added.
        """
        description = Path(description_path).read_text(encoding="utf-8")
        self.include_health_check_endpoint = include_health_check_endpoint
        self.app = FastAPI(
            title=service_name,
            version="0.0.1",
            contact={
                "name": "CDC Public Health Data Infrastructure",
                "url": "https://cdcgov.github.io/phdi-site/",
                "email": "dmibuildingblocks@cdc.gov",
            },
            license_info={
                "name": "Creative Commons Zero v1.0 Universal",
                "url": "https://creativecommons.org/publicdomain/zero/1.0/",
            },
            description=description,
        )

    def add_health_check_endpoint(self):
        @self.app.get("/")
        async def health_check() -> dict:
            """
            Check service status. If an HTTP 200 status code is returned along with
            '{"status": "OK"}' then the service is available and running properly.
            """
            return {"status": "OK"}

    def start(self) -> FastAPI:
        """
        Return a FastAPI instance with DIBBs metadata set. If
        `include_health_check_endpoint` is True, then the health check endpoint
        will be added.

        :return: The FastAPI instance.
        """
        if self.include_health_check_endpoint:
            self.add_health_check_endpoint()
        return self.app
