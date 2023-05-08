from dataclasses import dataclass
from enum import Enum
from importlib import metadata
from pathlib import Path
from typing import Callable, Optional

from fastapi import FastAPI


@dataclass
class LicenseInfo:
    """
    Represent license information.

    Attributes:
        name (str): The name of the license.
        url (str): The URL where the license can be found.
    """

    name: str
    url: str


# create a class with the DIBBs default Creative Commons Zero v1.0 and
# MIT license to be used by the BaseService class
class LicenseType(Enum):
    """
    Enum class to represent different types of licenses.
    Currently, it has CreativeCommonsZero (the DIBBs default)
    and MIT licenses.
    """

    CreativeCommonsZero = LicenseInfo(
        "Creative Commons Zero v1.0 Universal",
        "https://creativecommons.org/publicdomain/zero/1.0/",
    )
    MIT = LicenseInfo("The MIT License", "https://mit-license.org/")


@dataclass
class ContactInfo:
    """
    Represent contact information.

    Attributes:
        name (str): The name of the contact person or organization.
        url (str): The URL to the contact's website or information page.
        email (str): The contact's email address.
    """

    name: str
    url: str
    email: str


class BaseService:
    """
    Base class for all DIBBs services. This class provides a FastAPI instance with DIBBs
    metadata and optionally a health check endpoint.

    Attributes:
        LICENSE_INFO (LicenseAttributes): Default DIBBs Creative Commons
            Zero v1.0 license.
        DIBBS_CONTACT (ContactInfo): Default DIBBs contact information.
    """

    LICENSE_INFO = LicenseType.CreativeCommonsZero
    DIBBS_CONTACT = ContactInfo(
        "CDC Public Health Data Infrastructure",
        "https://cdcgov.github.io/phdi-site/",
        "dmibuildingblocks@cdc.gov",
    )

    def __init__(
        self,
        service_name: str,
        description_path: str,
        include_health_check_endpoint: bool = True,
        health_check_endpoint_path: str = "/",
        health_check_function: Optional[Callable] = None,
        license_info: Optional[LicenseType] = None,
        contact_info: Optional[ContactInfo] = None,
    ):
        """
        Initialize a BaseService instance.

        :param service_name: (str) The name of the service.
        :param description_path: (str) The path to a markdown file containing a
            description of the service.
        :param include_health_check_endpoint: (bool, optional) If True, the
            standard DIBBs health check endpoint will be added.
        :param health_check_endpoint_path: (str, optional) The path to the health
            check endpoint. Will allow for custom health check endpoints.
        :param health_check_function: (Optional[Callable], optional) An optional
            parameter to allow for a custom health check function.
        :param license_info: (Optional[LicenseType], optional) If empty, the
            standard DIBBs Creative Commons Zero v1.0 Universal license will be used.
            The other available option is to use the MIT license.
        :param contact_info: (Optional[ContactInfo], optional) If empty, the standard
            DIBBs contact info will be used.
        """
        description = Path(description_path).read_text(encoding="utf-8")
        self.include_health_check_endpoint = include_health_check_endpoint
        self.health_check_endpoint_path = health_check_endpoint_path
        self.health_check_function = health_check_function
        self.app = FastAPI(
            title=service_name,
            version=metadata.version("phdi"),
            contact=contact_info or self.DIBBS_CONTACT,
            license_info=license_info or self.LICENSE_INFO,
            description=description,
        )

    def add_health_check_endpoint(self) -> None:
        """Add health check endpoint to the FastAPI instance."""
        if self.health_check_function:
            health_check = self.health_check_function
        else:

            async def health_check() -> dict:
                """
                Check service status. If an HTTP 200 status code is returned along
                with '{"status": "OK"}' then the service is available and
                running properly.
                """
                return {"status": "OK"}

        self.app.get(self.health_check_endpoint_path)(health_check)

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
