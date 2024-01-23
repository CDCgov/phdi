import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict
from typing import List
from typing import Optional

from app import utils
from lxml import etree as ET


@dataclass
class Address:
    street_address_line_1: Optional[str] = None
    street_address_line_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    county: Optional[str] = None
    country: Optional[str] = None
    type: Optional[str] = None
    useable_period_low: Optional[str] = None
    useable_period_high: Optional[str] = None


@dataclass
class Name:
    prefix: Optional[str] = None
    first: Optional[str] = None
    middle: Optional[str] = None
    family: Optional[str] = None
    suffix: Optional[str] = None
    type: Optional[str] = None
    validTime_low: Optional[str] = None
    validTime_high: Optional[str] = None


@dataclass
class PHDCInputData:
    patient_address: List[Address] = None
    patient_name: List[Name] = None
    patient_administrative_gender_code: Optional[str] = None
    patient_race_code: Optional[str] = None
    patient_ethnic_group_code: Optional[str] = None
    patient_birth_time: Optional[str] = None


class PHDC:
    def __init__(self, header):
        self.header = header

    def to_xml_string(self):
        return ET.tostring(
            self.header,
            pretty_print=True,
            xml_declaration=True,
            encoding="utf-8",
        ).decode()


class PHDCBuilder:
    def __init__(self):
        self.input_data: PHDCInputData = None

    def set_input_data(self, input_data: PHDCInputData):
        self.input_data = input_data
        return self

    def _build_header(self):
        def get_type_id():
            type_id = ET.Element("typeId")
            type_id.set("root", "2.16.840.1.113883.1.3")
            type_id.set("extension", "POCD_HD000020")
            return type_id

        def get_id():
            id = ET.Element("id")
            id.set("root", "2.16.840.1.113883.19")
            id.set("extension", str(uuid.uuid4()))
            return id

        def get_effective_time():
            effective_time = ET.Element("effectiveTime")
            effective_time.set(
                "value", utils.get_datetime_now().strftime("%Y%m%d%H%M%S")
            )
            return effective_time

        class ConfidentialityCodes(str, Enum):
            normal = ("N",)
            restricted = ("R",)
            very_restricted = ("V",)

        def get_confidentiality_code(code: ConfidentialityCodes):
            confidentiality_code = ET.Element("confidentialityCode")
            confidentiality_code.set("code", code)
            confidentiality_code.set("codeSystem", "2.16.840.1.113883.5.25")
            return confidentiality_code

        def get_case_report_code():
            code = ET.Element("code")
            code.set("code", "55751-2")
            code.set("codeSystem", "2.16.840.1.113883.6.1")
            code.set("codeSystemName", "LOINC")
            code.set("displayName", "Public Health Case Report - PHRI")
            return code

        xsi_schema_location = ET.QName(
            "http://www.w3.org/2001/XMLSchema-instance", "schemaLocation"
        )

        namespace = {
            None: "urn:hl7-org:v3",
            "sdt": "urn:hl7-org:sdtc",
            "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        }
        clinical_document = ET.Element(
            "ClinicalDocument",
            {xsi_schema_location: "urn:hl7-org:v3 CDA_SDTC.xsd"},
            nsmap=namespace,
        )
        pi = ET.ProcessingInstruction(
            "xml-stylesheet", text='type="text/xsl" href="PHDC.xsl"'
        )
        clinical_document.addprevious(pi)

        clinical_document.append(get_type_id())
        clinical_document.append(get_id())
        clinical_document.append(get_case_report_code())
        clinical_document.append(get_effective_time())
        clinical_document.append(get_confidentiality_code(ConfidentialityCodes.normal))

        clinical_document.append(self._build_custodian(id=str(uuid.uuid4())))
        clinical_document.append(self._build_author(family_name="DIBBS"))

        return clinical_document

    def _build_telecom(
        self,
        **kwargs: dict,
        # phone: str,
        # use: Literal["HP", "WP", "MC"] = None,
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

        if "use" in kwargs.keys() and kwargs["use"] is not None:
            telecom_data.set("use", kwargs["use"])
        if "phone" in kwargs.keys() and kwargs["phone"] is not None:
            telecom_data.set("value", kwargs["phone"])

        return telecom_data

    def _build_addr(
        self,
        **kwargs,
        # use: Literal["H", "WP"] = None,
        # line: str = None,
        # city: str = None,
        # state: str = None,
        # zip: str = None,
        # county: str = None,
        # country: str = None,
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

        address_data = ET.Element("addr")
        if "use" in kwargs.keys() and kwargs["use"] is not None:
            address_data.set("use", kwargs["use"])

        for element, value in kwargs.items():
            if element != "use" and value is not None:
                if element == "line":
                    element = "streetAddressLine"
                elif element == "zip":
                    element = "postalCode"
                e = ET.Element(element)
                e.text = value
                address_data.append(e)

        return address_data

    def _build_name(
        self,
        **kwargs: dict,
        # use: Literal["L", "P"] = None,
        # prefix: str = None,
        # given_name: Union[str, List[str]] = None,
        # last_name: str = None,
    ):
        """
        Builds a `name` XML element for address data. There are two types of name
         uses: 'L' for legal and 'P' for pseudonym.

        :param use: Type of address, defaults to None.
        :param prefix: Name prefix, defaults to None.
        :param given_name: String or list of strings representing given name(s),
          defaults to None.
        :param last_name: Last name, defaults to None.
        :return: XML element of name data.
        """

        name_data = ET.Element("name")
        if "use" in kwargs.keys() and kwargs["use"] is not None:
            name_data.set("use", kwargs["use"])

        for element, value in kwargs.items():
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

    def _build_custodian(
        self,
        id: str,
    ):
        """
        Builds a `custodian` XML element for custodian data, which refers to the
          organization from which the PHDC originates and that is in charge of
          maintaining the document.

        :param id: Custodian identifier.
        :return: XML element of custodian data.
        """
        if id is None:
            raise ValueError("The Custodian id parameter must be a defined.")

        custodian_data = ET.Element("custodian")
        assignedCustodian = ET.Element("assignedCustodian")
        representedCustodianOrganization = ET.Element(
            "representedCustodianOrganization"
        )

        id_element = ET.Element("id")
        id_element.set("extension", id)
        representedCustodianOrganization.append(id_element)

        assignedCustodian.append(representedCustodianOrganization)
        custodian_data.append(assignedCustodian)

        return custodian_data

    def _build_author(self, family_name: str):
        """
        Builds an `author` XML element for author data, which represents the
            humans and/or machines that authored the document.

            This includes the OID as per HL7 standards, the family name of
            the author, which will be either the DIBBs project name or the
            origin/provenance of the data we're migrating as well as the
            creation timestamp of the document (not a parameter).

        :param family_name: The DIBBs project name or source of the data being migrated.
        :return: XML element of author data.
        """
        author_element = ET.Element("author")

        # time element with the current timestamp
        current_timestamp = utils.get_datetime_now().strftime("%Y%m%d%H%M%S")
        time_element = ET.Element("time")
        time_element.set("value", current_timestamp)
        author_element.append(time_element)

        # assignedAuthor element
        assigned_author = ET.Element("assignedAuthor")

        # using the standard OID for the author
        id_element = ET.Element("id")
        id_element.set("root", "2.16.840.1.113883.19.5")
        assigned_author.append(id_element)

        # family name is the example way to add either a project name or source of
        # the data being migrated
        name_element = ET.Element("name")
        family_element = ET.SubElement(name_element, "family")
        family_element.text = family_name

        assigned_author.append(name_element)

        author_element.append(assigned_author)

        return author_element

    def _build_coded_element(self, element_name: str, **kwargs: dict):
        """
        Builds coded elements, such as administrativeGenderCode, using kwargs code,
          codeSystem, and displayName.

        :param element_name: Name of the element being built.
        :param code: The element code, defaults to None
        :param codeSystem: The element codeSystem that the code corresponds to, defaults
          to None
        :param displayName: The element display name, defaults to None
        :return: XML element of coded data.
        """
        element = ET.Element(element_name)

        for e, v in kwargs.items():
            if e != "element_name" and v is not None:
                element.set(e, v)
        return element

    def _build_patient(self, **kwargs: dict):
        patient_data = ET.Element("patient")

        for element, value in kwargs.items():
            if value is not None:
                if isinstance(value, ET._Element):
                    patient_data.append(value)
                elif element in [
                    "administrativeGenderCode",
                    "raceCode",
                    "ethnicGroupCode",
                ]:
                    # TODO: Determine how to implement std:raceCode and/or stdc:raceCode
                    v = self._build_coded_element(
                        element,
                        **{"displayName": value},
                    )
                    patient_data.append(v)
                else:
                    e = ET.Element(element)
                    e.text = value
                    patient_data.append(e)

        return patient_data

    def _build_recordTarget(
        self,
        id: str,
        root: str = None,
        assigningAuthorityName: str = None,
        telecom_data_list: Optional[List[Dict]] = None,
        address_data_list: Optional[List[Dict]] = None,
        patient_data_list: Optional[List[Dict]] = None,
    ):
        """
        Builds a `recordTarget` XML element for recordTarget data, which refers to
          the medical record of the patient.

        :param id: recordTarget identifier
        :param root: recordTarget root
        :param assigningAuthorityName: recordTarget assigningAuthorityName
        :param telecom_data_list: XML data from _build_telecom
        :param address_data_list: XML data from _build_addr
        :param patient_data_list: XML data from _build_patient

        :raises ValueError: recordTarget needs ID to be defined.

        :return recordTarget_data: XML element of the recordTarget
        """
        if id is None:
            raise ValueError("The recordTarget id parameter must be a defined.")

        # create recordTarget element
        recordTarget_data = ET.Element("recordTarget")

        # Create and append 'patientRole' element
        patientRole = ET.Element("patientRole")
        recordTarget_data.append(patientRole)

        # add id data
        id_element = ET.Element("id")
        id_element.set("extension", id)

        # TODO: this should follow the same kwargs logic as above using
        #   the _build_coded_element logic
        if root is not None:
            id_element.set("root", root)

        if assigningAuthorityName is not None:
            id_element.set("assigningAuthorityName", assigningAuthorityName)
        patientRole.append(id_element)

        # add address data
        if address_data_list is not None:
            for address_data in address_data_list:
                if address_data is not None:
                    address_element = self._build_addr(address_data)
                    patientRole.append(address_element)

        # add telecom data
        if telecom_data_list is not None:
            for telecom_data in telecom_data_list:
                if telecom_data is not None:
                    telecom_element = self._build_telecom(telecom_data)
                    patientRole.append(telecom_element)

        # add patient data
        if patient_data_list is not None:
            for patient_data in patient_data_list:
                if patient_data is not None:
                    patient_element = self._build_patient(patient_data)
                    patientRole.append(patient_element)

        return recordTarget_data

    def build(self):
        return PHDC(self._build_header())
