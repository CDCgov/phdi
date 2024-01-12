from typing import Literal

from lxml import etree as ET


class PHDC:
    def __init__(self, builder):
        self.header = builder.header


class PHDCBuilder:
    def __init__(self):
        self.header = None

    def _build_telecom(
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

        :param use: _description_, defaults to None
        :param line: _description_, defaults to None
        :param city: _description_, defaults to None
        :param state: _description_, defaults to None
        :param zip: _description_, defaults to None
        :param county: _description_, defaults to None
        :param country: _description_, defaults to None
        :return: XML element of address data.
        """
        address_elements = locals()

        address_data = ET.Element("addr")
        if use is not None:
            address_data.set("use", use)

        for element, value in address_elements.items():
            if element != "use" and value is not None:
                if element == "line":
                    element = "streetAddressLine"
                elif element == "zip":
                    element = "postalCode"
                e = ET.Element(element)
                e.text = value
                address_data.append(e)

        return address_data

    def build(self):
        return PHDC(self)
