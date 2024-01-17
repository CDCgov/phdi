from __future__ import annotations

from typing import Literal

from lxml import etree as ET


class PHDC:
    def __init__(self, builder: PHDCBuilder) -> None:
        self.header = builder.header

    def to_xml_string(self):
        return ET.tostring(self.header) if self.header is not None else ""


class PHDCBuilder:
    def __init__(self) -> None:
        self.header = None

    def _build_telecom(
        self,
        phone: str,
        use: Literal["HP", "WP", "MC"] = None,
    ):
        """
        Builds a `telecom` XML element for phone data including phone number (as
        `value`) and use, if available. There are three types of phone uses: 'HP'
        for home phone, 'WP' for work phone, and 'MC' for mobile phone.

        :param phone: The phone number.
        :param use: Type of phone number, defaults to None.
        :return: XML element of telecom data.
        """
        telecom_data = ET.Element("telecom")

        if use is not None:
            telecom_data.set("use", use)
        telecom_data.set("value", phone)

        return telecom_data

    def _build_addr(
        self,
        use: Literal["H", "WP"] = None,
        line: str = None,
        city: str = None,
        state: str = None,
        zip: str = None,
        county: str = None,
        country: str = None,
    ):
        """
        Builds an `addr` XML element for address data. There are two types of address
         uses: 'H' for home address and 'WP' for workplace address.

        :param use: Type of address, defaults to None.
        :param line: Street address, defaults to None.
        :param city: City, defaults to None.
        :param state: State, defaults to None.
        :param zip: Zip code, defaults to None.
        :param county: County, defaults to None.
        :param country: Country, defaults to None.
        :return: XML element of address data.
        """
        address_elements = locals()

        address_data = ET.Element("addr")
        if use is not None:
            address_data.set("use", use)

        for element, value in address_elements.items():
            if element not in ["use", "self"] and value is not None:
                if element == "line":
                    element = "streetAddressLine"
                elif element == "zip":
                    element = "postalCode"
                e = ET.Element(element)
                e.text = value
                address_data.append(e)

        return address_data

    def build(self, **kwargs) -> PHDC:
        return PHDC(self)


class PHDCDirector:
    def __init__(self, builder: PHDCBuilder) -> None:
        self.builder = builder

    def build_case_report(self, telecom_data: dict, addr_data: dict) -> PHDC:
        """
        Builds a case report PHDC object.

        Arguments are dictionaries passed to PHDCBuilder's methods and should include
        the arguments required by those methods. See PHDCBuilder's methods for more
        info.

        :param telecom_data: Dictionary of telecom data.
        :param addr_data: Dictionary of address data.
        :return: PHDC object.
        """
        telecom_element = self.builder._build_telecom(**telecom_data)
        addr_element = self.builder._build_addr(**addr_data)
        return self.builder.build(telecom=telecom_element, addr=addr_element)

    # TODO: find out if source data we will use requires building separate lab reports
