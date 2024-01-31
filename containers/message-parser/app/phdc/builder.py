import uuid
from typing import List
from typing import Literal
from typing import Optional

from app import utils
from app.phdc.models import Address
from app.phdc.models import Name
from app.phdc.models import Observation
from app.phdc.models import Patient
from app.phdc.models import PHDCInputData
from app.phdc.models import Telecom
from lxml import etree as ET


class PHDC:
    """
    A class to represent a Public Health Data Container (PHDC) document given a
    PHDCBuilder.
    """

    def __init__(self, data: ET.ElementTree = None):
        """
        Initializes the PHDC class with a PHDCBuilder.

        :param builder: The PHDCBuilder to use to build the PHDC.
        """
        self.data = data

    def to_xml_string(self) -> bytes:
        """
        Return a string representation of the PHDC XML document as serialized bytes.
        """
        if self.data is None:
            raise ValueError("The PHDC object must be initialized.")
        return ET.tostring(
            self.data,
            pretty_print=True,
            xml_declaration=True,
            encoding="utf-8",
        ).decode()


class PHDCBuilder:
    """
    A builder class for creating PHDC documents.
    """

    def __init__(self):
        """
        Initializes the PHDCBuilder class and create and empty PHDC.
        """

        self.input_data: PHDCInputData = None
        self.phdc = self._build_base_phdc()

    def set_input_data(self, input_data: PHDCInputData):
        """
        Given a PHDCInputData object, set the input data for the PHDCBuilder.

        :param input_data: The PHDCInputData object to use as input data.
        """

        self.input_data = input_data

    def _build_base_phdc(self) -> ET.ElementTree:
        """
        Create the base PHDC XML document.
        """
        ET.register_namespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")

        xsi_schema_location = ET.QName(
            "http://www.w3.org/2001/XMLSchema-instance", "schemaLocation"
        )

        namespace = {
            None: "urn:hl7-org:v3",
            "sdt": "urn:hl7-org:sdtc",
            "sdtcxmlnamespaceholder": "urn:hl7-org:v3",
            "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        }
        clinical_document = ET.Element(
            "ClinicalDocument",
            {xsi_schema_location: "urn:hl7-org:v3 CDA_SDTC.xsd"},
            nsmap=namespace,
        )
        clinical_document = ET.ElementTree(clinical_document)
        pi = ET.ProcessingInstruction(
            "xml-stylesheet", text='type="text/xsl" href="PHDC.xsl"'
        )

        clinical_document.getroot().addprevious(pi)

        return clinical_document

    def _get_type_id(self) -> ET.Element:
        """
        Returns the type ID element of the PHDC header.
        """
        type_id = ET.Element("typeId")
        type_id.set("root", "2.16.840.1.113883.1.3")
        type_id.set("extension", "POCD_HD000020")
        return type_id

    def _get_id(self) -> ET.Element:
        """
        Returns the ID element of the PHDC header.
        """
        id = ET.Element("id")
        id.set("root", "2.16.840.1.113883.19")
        id.set("extension", str(uuid.uuid4()))
        return id

    def _get_effective_time(self) -> ET.Element:
        """
        Returns the effectiveTime element of the PHDC header.
        """
        effective_time = ET.Element("effectiveTime")
        effective_time.set("value", utils.get_datetime_now().strftime("%Y%m%d%H%M%S"))
        return effective_time

    def _get_confidentiality_code(
        self, confidentiality: Literal["normal", "restricted", "very restricted"]
    ) -> ET.Element:
        """
        Returns the confidentialityCode element of the PHDC header.

        :param confidentiality: The confidentiality code to use.
        """
        confidendiality_codes = {
            "normal": "N",
            "restricted": "R",
            "very restricted": "V",
        }

        confidentiality_code = ET.Element("confidentialityCode")
        confidentiality_code.set("code", confidendiality_codes[confidentiality])
        confidentiality_code.set("codeSystem", "2.16.840.1.113883.5.25")
        return confidentiality_code

    def _get_clinical_info_code(self):
        """
        Returns the code element of the header for a PHDC case report.
        """
        code = ET.Element("code")
        code.set("code", "55751-2")
        code.set("codeSystem", "2.16.840.1.113883.6.1")
        code.set("codeSystemName", "LOINC")
        code.set("displayName", "Public Health Case Report - PHRI")
        return code

    def _get_title(self):
        """
        Returns the title element of the PHDC header.
        """
        title = ET.Element("title")
        title.text = (
            "Public Health Case Report - Data from the DIBBs FHIR to PHDC Converter"
        )
        return title

    def build_header(self):
        """
        Builds the header of the PHDC document.
        """
        root = self.phdc.getroot()
        root.append(self._get_type_id())
        root.append(self._get_id())
        root.append(self._get_clinical_info_code())
        root.append(self._get_title())
        root.append(self._get_effective_time())
        root.append(self._get_confidentiality_code(confidentiality="normal"))

        root.append(self._build_custodian(id=str(uuid.uuid4())))
        root.append(self._build_author(family_name="DIBBS"))
        root.append(
            self._build_recordTarget(
                id=str(uuid.uuid4()),
                root="2.16.840.1.113883.4.1",
                assigningAuthorityName="LR",
                telecom_data=self.input_data.patient.telecom,
                address_data=self.input_data.patient.address,
                patient_data=self.input_data.patient,
            )
        )

    def build_body(self):
        body = ET.Element("component")
        structured_body = ET.Element("structuredBody")
        body.append(structured_body)

        match self.input_data.type:
            case "case_report":
                clinical_info = self._build_clinical_info(self.input_data.clinical_info)
                body.append(clinical_info)
            case "contact_record":
                pass
            case "lab_report":
                pass
            case "morbidity_report":
                pass

        self.phdc.getroot().append(body)

    def _build_clinical_info(
        self, observation_data: Optional[List[Observation]] = None
    ) -> ET.Element:
        component = ET.Element("component")
        section = ET.Element("section")
        id = ET.Element("id")
        id.set("extension", str(uuid.uuid4()))
        id.set("assigningAuthorityName", "LR")

        code = ET.Element("code")
        code.set("code", "55752-0")
        code.set("codeSystem", "2.16.840.1.113883.6.1")
        code.set("codeSystemName", "LOINC")
        code.set("displayName", "Clinical Information")

        title = ET.Element("title")
        title.text = "Clinical Information"

        section.append(id)
        section.append(code)
        section.append(title)

        # add observation data to section
        if observation_data:
            for observation in observation_data:
                observation_element = self._build_observation(observation)
                section.append(observation_element)

        component.append(section)
        return component

    def _build_telecom(self, telecom: Telecom) -> ET.Element:
        """
        Builds a `telecom` XML element for phone data including phone number (as
        `value`) and use, if available. There are three types of phone uses: 'HP'
        for home phone, 'WP' for work phone, and 'MC' for mobile phone.

        :param telecom: The data for building the telecom element as a Telecom object.
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

    def _add_field(self, parent_element: ET.Element, data: str, field_name: str):
        """
        Adds a child element to a parent element given the data and field name.

        :param parent_element: The parent element to add the child element to.
        :param data: The data to add to the child element.
        :param field_name: The name of the child element.
        """
        if data is not None:
            e = ET.Element(field_name)
            e.text = data
            parent_element.append(e)

    def _build_observation(self, observation: Observation) -> ET.Element:
        """
        Creates Entry XML element for observation data.

        :param observation: The data for building the observation element as an
        Entry object.
        :return entry_data: XML element of Entry data
        """
        # Create the 'entry' element
        entry_data = ET.Element("entry", {"typeCode": observation.type_code})

        # Create the 'observation' element and append it to 'entry'
        observation_data = ET.SubElement(
            entry_data,
            "observation",
            {"classCode": observation.class_code, "moodCode": observation.mood_code},
        )

        if observation.code:
            code_element_xml = self._build_coded_element(
                "code", **observation.code.to_attributes()
            )
            observation_data.append(code_element_xml)

        # Add attributes to 'observation' using CodedElement for value
        if observation.value:
            value_element_xml = self._build_coded_element(
                "value", **observation.value.to_attributes()
            )
            observation_data.append(value_element_xml)

        # Add 'translation' elements to 'value' if translation is provided
        if observation.translation:
            translation_element_xml = self._build_coded_element(
                "translation", **observation.translation.to_attributes()
            )
            value_element_xml.append(translation_element_xml)

        return entry_data

    def _build_addr(
        self,
        address: Address,
    ) -> ET.Element:
        """
        Builds an `addr` XML element for address data. There are two types of address
         uses: 'H' for home address and 'WP' for workplace address.

        :param address: The data for building the address element as an Address object.
        :return: XML element of address data.
        """
        address_data = ET.Element("addr")

        if address.type is not None:
            address_data.set("use", "H" if address.type.lower() == "home" else "WP")

        self._add_field(
            address_data, address.street_address_line_1, "streetAddressLine"
        )
        self._add_field(
            address_data, address.street_address_line_2, "streetAddressLine"
        )
        self._add_field(address_data, address.city, "city")
        self._add_field(address_data, address.state, "state")
        self._add_field(address_data, address.postal_code, "postalCode")
        self._add_field(address_data, address.county, "county")
        self._add_field(address_data, address.country, "country")

        return address_data

    def _build_name(self, name: Name) -> ET.Element:
        """
        Builds a `name` XML element for name data.

        :param name: The data for constructing the name element as a Name object.
        :return: XML element of name data.
        """

        name_data = ET.Element("name")

        if name.type is not None:
            types = {
                "official": "L",
                "usual": "L",
                "maiden": "P",
                "nickname": "P",
                "pseudonym": "P",
            }
            name_data.set("use", types[name.type])

        self._add_field(name_data, name.prefix, "prefix")
        self._add_field(name_data, name.first, "given")
        self._add_field(name_data, name.middle, "given")
        self._add_field(name_data, name.family, "family")
        self._add_field(name_data, name.suffix, "suffix")

        return name_data

    def _build_custodian(
        self,
        id: str,
    ) -> ET.Element:
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

    def _build_author(self, family_name: str) -> ET.Element:
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

    def _build_coded_element(self, element_name: str, **kwargs: dict) -> ET.Element:
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

    def _build_patient(self, patient: Patient) -> ET.Element:
        """
        Given a Patient object, build the patient element of the PHDC.

        :param patient: The Patient object to use for building the patient element.
        """

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
    ) -> ET.Element:
        """
        Builds a `recordTarget` XML element for recordTarget data, which refers to
          the medical record of the patient.

        :param id: recordTarget identifier
        :param root: recordTarget root
        :param assigningAuthorityName: recordTarget assigningAuthorityName
        :param telecom_data: Telecom data from _build_telecom
        :param address_data: Address data from _build_addr
        :param patient_data: Patient data from _build_patient

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

    def build(self) -> PHDC:
        """
        Returns a PHDC object.
        """
        self.build_header()
        self.build_body()
        return PHDC(data=self.phdc)
