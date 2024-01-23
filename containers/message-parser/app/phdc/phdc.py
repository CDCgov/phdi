import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List
from typing import Optional

from app import utils
from lxml import etree as ET


@dataclass
class Telecom:
    value: Optional[str] = None
    type: Optional[str] = None
    useable_period_low: Optional[str] = None
    useable_period_high: Optional[str] = None


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
class Patient:
    name: List[Name] = None
    address: List[Address] = None
    telecom: List[Telecom] = None
    administrative_gender_code: Optional[str] = None
    race_code: Optional[str] = None
    ethnic_group_code: Optional[str] = None
    birth_time: Optional[str] = None


@dataclass
class PHDCInputData:
    type: str = "case report"
    patient: Patient = None


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
        clinical_document.append(
            self._build_recordTarget(
                id=str(uuid.uuid4()),
                assigningAuthorityName="L",
                telecom_data=self.input_data.patient.telecom,
                address_data=self.input_data.patient.address,
                patient_data=self.input_data.patient,
            )
        )
        return clinical_document

    def _build_telecom(
        self,
        telecom: Telecom
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

        if telecom.type is not None:
            types = {
                "home": "H",
                "work": "WP",
                "mobile": "MC",
            }
            telecom_data.set("use", types[telecom.type])

        if telecom.value is not None:
            if telecom.type in ["home", "work", "mobile"]:
                telecom_data.set("value", f"tel:{telecom.value}")
            elif telecom.type == "email":
                telecom_data.set("value", f"mailto:{telecom.value}")
            else:
                telecom_data.set("value", telecom.value)

        return telecom_data

    def _build_addr(
        self,
        address: Address,
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

        def add_field(data, field_name: str):
            if data is not None:
                e = ET.Element(field_name)
                e.text = data
                address_data.append(e)

        if address.type is not None:
            address_data.set("use", "H" if address.type.lower() == "home" else "WP")

        add_field(address.street_address_line_1, "streetAddressLine")
        add_field(address.street_address_line_2, "streetAddressLine")
        add_field(address.city, "city")
        add_field(address.state, "state")
        add_field(address.postal_code, "postalCode")
        add_field(address.county, "county")
        add_field(address.country, "country")

        return address_data

    def _build_name(
        self,
        name: Name
        # **kwargs: dict,
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

        def add_field(data, field_name: str):
            if data is not None:
                e = ET.Element(field_name)
                e.text = data
                name_data.append(e)

        if name.type is not None:
            types = {
                "legal": "L",
                "pseudonym": "P",
            }
            name_data.set("use", types[name.type])

        add_field(name.prefix, "prefix")
        add_field(name.first, "given")
        add_field(name.middle, "given")
        add_field(name.family, "family")
        add_field(name.suffix, "suffix")

        # for element, value in kwargs.items():
        #     if element != "use" and value is not None:
        #         if element == "given_name":
        #             element = "given"
        #
        #             # Split single string names into first name and middle names as
        #             # PHDC appears to only allow for up to two given names
        #             if isinstance(value, str) and len(value.split()) > 1:
        #                 value = [
        #                     value.split()[0],
        #                     " ".join(v for v in (value.split()[1:])),
        #                 ]
        #
        #         elif element == "last_name":
        #             element = "family"
        #
        #         # Append each value of a list, e.g., given name, as its own Element
        #         if isinstance(value, list):
        #             value = [
        #                 value[0],
        #                 " ".join(v for v in (value[1:])),
        #             ]
        #             for v in value:
        #                 e = ET.Element(element)
        #                 e.text = v
        #                 name_data.append(e)
        #         else:
        #             e = ET.Element(element)
        #             e.text = value
        #             name_data.append(e)

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

    def _build_patient(self, patient: Patient):
        patient_data = ET.Element("patient")

        for name in patient.name:
            patient_data.append(self._build_name(name))

        if patient.administrative_gender_code is not None:
            v = self._build_coded_element(
                "administrativeGenderCode",
                **{"displayName": patient.administrative_gender_code},
            )
            patient_data.append(v)

        if patient.race_code is not None:
            v = self._build_coded_element(
                "raceCode",
                **{"displayName": patient.race_code},
            )
            patient_data.append(v)

        if patient.ethnic_group_code is not None:
            v = self._build_coded_element(
                "ethnicGroupCode",
                **{"displayName": patient.ethnic_group_code},
            )
            patient_data.append(v)

        if patient.birth_time is not None:
            e = ET.Element("birthTime")
            e.text = patient.birth_time
            patient_data.append(e)
        # TODO: Determine how to implement std:raceCode and/or stdc:raceCode

        return patient_data

    def _build_recordTarget(
        self,
        id: str,
        root: str = None,
        assigningAuthorityName: str = None,
        telecom_data: Optional[List[Telecom]] = None,
        address_data: Optional[List[Address]] = None,
        patient_data: Optional[Patient] = None,
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
        if address_data is not None:
            for address_data in address_data:
                if address_data is not None:
                    address_element = self._build_addr(address_data)
                    patientRole.append(address_element)

        # add telecom data
        if telecom_data is not None:
            for telecom_data in telecom_data:
                if telecom_data is not None:
                    telecom_element = self._build_telecom(telecom_data)
                    patientRole.append(telecom_element)

        # add patient data
        if patient_data is not None:
            patient_element = self._build_patient(patient_data)
            patientRole.append(patient_element)

        return recordTarget_data

    def build(self):
        return PHDC(self._build_header())
