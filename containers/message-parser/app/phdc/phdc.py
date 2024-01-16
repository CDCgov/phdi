from __future__ import annotations

from typing import Literal
from typing import Optional

from lxml import etree as ET


class PHDC:
    def __init__(self, builder: PHDCBuilder) -> None:
        self.header = builder.header


class PHDCBuilder:
    def __init__(self) -> None:
        self.header = None

    def _build_telecom(
        phone: str,
        use: Optional[Literal["HP", "WP", "MC"]] = None,
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

    def build(self) -> PHDC:
        return PHDC(self)


class PHDCDirector:
    def __init__(self, builder: PHDCBuilder) -> None:
        self.builder = builder

    def build_case_report(
        self, phone: str, use: Optional[Literal["HP", "WP", "MC"]] = None
    ) -> PHDC:
        self.builder._build_telecom(phone, use)
        return self.builder.build()

    # TODO: find out if source data we will use requires building separate lab reports
    def build_lab_report(
        self, phone: str, use: Optional[Literal["HP", "WP", "MC"]] = None
    ) -> PHDC:
        self.builder._build_telecom(phone, use)
        return self.builder.build()
