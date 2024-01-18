from __future__ import annotations

from typing import List
from typing import Literal
from typing import Optional
from typing import Union

from dataclass import dataclass
from lxml import etree as ET


@dataclass
class PHDCData:
    phone_use: Optional[str] = None
    phone: Optional[str] = None
    addr_use: Optional[str] = None
    addr_line: Optional[str] = None
    addr_city: Optional[str] = None
    addr_state: Optional[str] = None
    addr_zip: Optional[str] = None
    addr_county: Optional[str] = None
    addr_country: Optional[str] = None
    name_use: Optional[str] = None
    name_prefix: Optional[str] = None
    given_name: str = None
    last_name: str = None


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

    def _build_name(
        use: Literal["L", "P"] = None,
        prefix: str = None,
        given_name: Union[str, List[str]] = None,
        last_name: str = None,
    ):
        """
        Builds a `name` XML element for address data. There are two types of name
         uses: 'L' for legal and 'P' for pseudonym.

        :param use: Type of address, defaults to None.
        :param prefix: Name prefix, defaults to None.
        :param given_name: String or list of strings representing given name(s),
          defaults to None.
        :param last_name: Last name, defaults to None.
        """
        name_elements = locals()

        name_data = ET.Element("name")
        if use is not None:
            name_data.set("use", use)

        for element, value in name_elements.items():
            if element != "use" and value is not None:
                if element == "given_name":
                    element = "given"

                    # Split single string names into first name and middle names as
                    # PHDC appears to only allow for up to two given names
                    if isinstance(value, str) and len(value.split()) > 1:
                        value = [
                            value.split()[0],
                            " ".join(v for v in (value.split()[1:])),
                        ]

                elif element == "last_name":
                    element = "family"

                # Append each value of a list, e.g., given name, as its own Element
                if isinstance(value, list):
                    value = [
                        value[0],
                        " ".join(v for v in (value[1:])),
                    ]
                    for v in value:
                        e = ET.Element(element)
                        e.text = v
                        name_data.append(e)
                else:
                    e = ET.Element(element)
                    e.text = value
                    name_data.append(e)

        return name_data

    def build(self, **kwargs) -> PHDC:
        return PHDC(self)


class PHDCDirector:
    def __init__(self, builder: PHDCBuilder) -> None:
        self.builder = builder

    def build_case_report(self, data: PHDCData) -> PHDC:
        """
        Builds a case report PHDC object.

        Arguments are dictionaries passed to PHDCBuilder's methods and should include
        the arguments required by those methods. See PHDCBuilder's methods for more
        info.

        :param data: Dictionary of parsed data to be used to construct a PHDC
            Case Report.
        :return: PHDC object.
        """
        telecom_data = {"phone": data.phone, "use": data.phone_use}

        # Extracting address data
        addr_data = {
            "use": data.addr_use,
            "line": data.addr_line,
            "city": data.addr_city,
            "state": data.addr_state,
            "zip": data.addr_zip,
            "county": data.addr_county,
            "country": data.addr_country,
        }

        telecom_element = self.builder._build_telecom(**telecom_data)
        addr_element = self.builder._build_addr(**addr_data)
        return self.builder.build(telecom=telecom_element, addr=addr_element)

    # TODO: find out if source data we will use requires building separate lab reports
