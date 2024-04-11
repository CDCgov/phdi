from importlib import metadata
from pathlib import Path
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

# create a class with the DIBBs default Creative Commons Zero v1.0 and
# MIT license to be used by the BaseService class
LICENSES = {
    "CreativeCommonsZero": {
        "name": "Creative Commons Zero v1.0 Universal",
        "url": "https://creativecommons.org/publicdomain/zero/1.0/",
    },
    "MIT": {"name": "The MIT License", "url": "https://mit-license.org/"},
}

DIBBS_CONTACT = {
    "name": "CDC Public Health Data Infrastructure",
    "url": "https://cdcgov.github.io/phdi-site/",
    "email": "dmibuildingblocks@cdc.gov",
}


STATUS_OK = {"status": "OK"}


class StatusResponse(BaseModel):
    """
    The schema for the response from the health check endpoint.
    """

    status: Literal["OK"]


class BaseService:
    def __init__(
        self,
        service_name: str,
        service_path: str,
        description_path: str,
        include_health_check_endpoint: bool = True,
        license_info: Literal["CreativeCommonsZero", "MIT"] = "CreativeCommonsZero",
    ):
        """
        Initialize a BaseService instance.

        :param service_name: The name of the service.
        :param service_path: The path to used to access the service from a gateway.
        :param description_path: The path to a markdown file containing a description of
            the service.
        :param include_health_check_endpoint: If True, the standard DIBBs health check
            endpoint will be added.
        :param license_info: If empty, the standard DIBBs Creative Commons Zero v1.0
            Universal license will be used. The other available option is to use the
            MIT license.
        """
        description = Path(description_path).read_text(encoding="utf-8")
        self.service_path = service_path
        self.include_health_check_endpoint = include_health_check_endpoint
        self.app = FastAPI(
            title=service_name,
            version=metadata.version("phdi"),
            contact=DIBBS_CONTACT,
            license_info=LICENSES[license_info],
            description=description,
        )

    def add_path_rewrite_middleware(self):
        """
        Add middleware to the FastAPI instance to strip the service_path
        from the URL path if it is present. This is useful when the service
        is behind a gateway that is using a path-based routing strategy.
        """

        @self.app.middleware("http")
        async def rewrite_path(request, call_next):
            if request.url.path.startswith(self.service_path):
                request.scope["path"] = request.scope["path"].replace(
                    self.service_path, ""
                )
                if request.scope["path"] == "":
                    request.scope["path"] = "/"
            return await call_next(request)

    def add_health_check_endpoint(self):
        @self.app.get("/")
        async def health_check() -> StatusResponse:
            """
            Check service status. If an HTTP 200 status code is returned along with
            '{"status": "OK"}' then the service is available and running properly.
            """
            return STATUS_OK

    def start(self) -> FastAPI:
        """
        Return a FastAPI instance with DIBBs metadata set. If
        `include_health_check_endpoint` is True, then the health check endpoint
        will be added.

        :return: The FastAPI instance.
        """
        self.add_path_rewrite_middleware()
        if self.include_health_check_endpoint:
            self.add_health_check_endpoint()
        return self.app
