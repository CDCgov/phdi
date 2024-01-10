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
        `value`) and use, if available.

        :param phone: The phone number.
        :param use: Type of phone number, defaults to None.
        :return: XML element of telecom data.
        """
        telecom_data = ET.Element("telecom")

        if use is not None:
            telecom_data.set("use", use)
        telecom_data.set("value", phone)

        return telecom_data

    def build(self):
        return PHDC(self)
