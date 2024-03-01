import json
import pathlib
import uuid
from datetime import date
from unittest.mock import patch

import pytest
from app import utils
from app.phdc.builder import PHDCBuilder
from app.phdc.models import Address
from app.phdc.models import CodedElement
from app.phdc.models import Name
from app.phdc.models import Observation
from app.phdc.models import Organization
from app.phdc.models import Patient
from app.phdc.models import PHDCInputData
from app.phdc.models import Telecom
from lxml import etree as ET
from xmldiff import formatting
from xmldiff import main as xmldiff


def read_json_from_test_assets(filename: str) -> dict:
    """
    Reads a JSON file from the test assets directory.

    :param filename: The name of the file to read.
    :return: A dictionary containing the contents of the file.
    """
    return json.load(open((pathlib.Path(__file__).parent.parent / "assets" / filename)))


def read_file_from_test_assets(filename: str) -> str:
    """
    Reads a file from the test assets directory.

    :param filename: The name of the file to read.
    :return: A string containing the contents of the file.
    """
    with open(
        (pathlib.Path(__file__).parent.parent / "tests" / "assets" / filename), "r"
    ) as file:
        return file.read()


def parse_file_from_test_assets(filename: str) -> ET.ElementTree:
    """
    Parses a file from the assets directory into an ElementTree.

    :param filename: The name of the file to read.
    :return: An ElementTree containing the contents of the file.
    """
    with open(
        (pathlib.Path(__file__).parent.parent / "tests" / "assets" / filename), "r"
    ) as file:
        parser = ET.XMLParser(remove_blank_text=True)
        tree = ET.parse(
            file,
            parser,
        )
        return tree


@pytest.mark.parametrize(
    "build_telecom_test_data, expected_result",
    [
        # Success with `use`
        (
            Telecom(value="+1-800-555-1234", type="work"),
            '<telecom use="WP" value="tel:+1-800-555-1234"/>',
        ),
        # Success without `use`
        (
            Telecom(value="+1-800-555-1234"),
            '<telecom value="+1-800-555-1234"/>',
        ),
        # Success with `use` as None
        (
            Telecom(value="+1-800-555-1234", type=None),
            '<telecom value="+1-800-555-1234"/>',
        ),
    ],
)
def test_build_telecom(build_telecom_test_data, expected_result):
    builder = PHDCBuilder()
    xml_telecom_data = builder._build_telecom(build_telecom_test_data)
    assert ET.tostring(xml_telecom_data).decode() == expected_result


@pytest.mark.parametrize(
    "element_name, kwargs, expected_xml",
    [
        # test case for normal handling
        (
            "element",
            {
                "code": "someCode",
                "codeSystem": "someCodeSystem",
                "displayName": "someDisplayName",
            },
            '<element code="someCode" codeSystem="someCodeSystem" '
            'displayName="someDisplayName"/>',
        ),
        # test xsi_type "TS" where the date value is set to the value attribute
        (
            "value",
            {
                "{http://www.w3.org/2001/XMLSchema-instance}type": "TS",
                "value": "20240101",
            },
            '<value xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            'xsi:type="TS" value="20240101"/>',
        ),
    ],
)
def test_build_coded_element(element_name, kwargs, expected_xml):
    builder = PHDCBuilder()
    result_element = builder._build_coded_element(element_name, **kwargs)
    result_xml = ET.tostring(result_element).decode()
    assert result_xml == expected_xml


@pytest.mark.parametrize(
    "build_observation_test_data, expected_result",
    [
        # Test case with a single code element, value, and translation
        (
            Observation(
                type_code="COMP",
                class_code="OBS",
                mood_code="EVN",
                code=CodedElement(code="1", code_system="0", display_name="Code"),
                value=CodedElement(
                    xsi_type="ST", code="2", code_system="1", display_name="V"
                ),
                translation=CodedElement(
                    xsi_type="T", code="0", code_system="L", display_name="T"
                ),
            ),
            (
                '<observation classCode="OBS" moodCode="EVN"><code code="1" '
                + 'codeSystem="0" displayName="Code"/><value xsi:type="ST" code="2" '
                + 'codeSystem="1" displayName="V"><translation xsi:type="T" code="0" '
                + 'codeSystem="L" displayName="T"/></value></observation>'
                '<observation classCode="OBS" moodCode="EVN"><code code="1" '
                + 'codeSystem="0" displayName="Code"/><value xsi:type="ST" code="2" '
                + 'codeSystem="1" displayName="V"><translation xsi:type="T" code="0" '
                + 'codeSystem="L" displayName="T"/></value></observation>'
            ),
        )
    ],
)
def test_build_observation(build_observation_test_data, expected_result):
    builder = PHDCBuilder()
    xod = builder._build_observation(build_observation_test_data)
    actual_result = ET.tostring(xod, encoding="unicode").replace(
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ', ""
    )
    # TODO: There has to be a more elegant way to do that...
    assert actual_result == expected_result


@pytest.mark.parametrize(
    "build_addr_test_data, expected_result",
    [
        # Success with all values present
        (
            Address(
                type="Home",
                street_address_line_1="123 Main Street",
                city="Brooklyn",
                state="New York",
                postal_code="11205",
                county="Kings",
                country="USA",
            ),
            (
                '<addr use="H"><streetAddressLine>123 Main Street</streetAddressLine>'
                + "<city>Brooklyn</city><state>New York</state>"
                + "<postalCode>11205</postalCode><county>Kings</county>"
                + "<country>USA</country></addr>"
            ),
        ),
        # Success with some values missing
        (
            Address(
                type="Home",
                street_address_line_1="123 Main Street",
                city="Brooklyn",
                state="New York",
            ),
            (
                '<addr use="H"><streetAddressLine>123 Main Street</streetAddressLine>'
                + "<city>Brooklyn</city><state>New York</state></addr>"
            ),
        ),
        # Success with some values as None
        (
            Address(
                type="Home",
                street_address_line_1="123 Main Street",
                city="Brooklyn",
                state=None,
            ),
            (
                '<addr use="H"><streetAddressLine>123 Main Street</streetAddressLine>'
                + "<city>Brooklyn</city></addr>"
            ),
        ),
    ],
)
def test_build_addr(build_addr_test_data, expected_result):
    builder = PHDCBuilder()
    xml_addr_data = builder._build_addr(build_addr_test_data)
    assert ET.tostring(xml_addr_data).decode() == expected_result


@pytest.mark.parametrize(
    "build_name_test_data, expected_result",
    [
        # Success with all single given_name
        (
            Name(type="official", prefix="Mr.", first="John", family="Doe"),
            (
                '<name use="L"><prefix>Mr.</prefix>'
                + "<given>John</given><family>Doe</family></name>"
            ),
        ),
        # Success with given_name as list
        (
            Name(
                type="usual", prefix="Mr.", first="John", middle="Jacob", family="Doe"
            ),
            (
                '<name use="L"><prefix>Mr.</prefix>'
                + "<given>John</given><given>Jacob</given><family>Doe</family></name>"
            ),
        ),
        # Success with more than 2 given names in a string condensed to 2 given names
        (
            Name(
                type="official",
                prefix="Mr.",
                first="John",
                middle="Jacob Jingleheimer",
                family="Doe",
                suffix="V",
            ),
            (
                '<name use="L"><prefix>Mr.</prefix>'
                + "<given>John</given><given>Jacob Jingleheimer</given>"
                + "<family>Doe</family>"
                + "<suffix>V</suffix></name>"
            ),
        ),
    ],
)
def test_build_name(build_name_test_data, expected_result):
    builder = PHDCBuilder()
    xml_name_data = builder._build_name(build_name_test_data)
    assert ET.tostring(xml_name_data).decode() == expected_result


@pytest.mark.parametrize(
    "build_custodian_test_data, expected_result",
    [
        # Success with `id` only
        (
            [Organization(id="TEST ID")],
            (
                "<custodian>\n"
                "  <assignedCustodian>\n"
                "    <representedCustodianOrganization>\n"
                '      <id extension="TEST ID"/>\n'
                "    </representedCustodianOrganization>\n"
                "  </assignedCustodian>\n"
                "</custodian>\n"
            ),
        ),
        # Success with data
        (
            [
                Organization(
                    id="112233",
                    name="Happy Labs",
                    telecom=Telecom(value="8888675309"),
                    address=Address(
                        street_address_line_1="23 main st",
                        street_address_line_2="apt 12",
                        city="Fort Worth",
                        state="Texas",
                        postal_code="76006",
                        county="Tarrant",
                        country="USA",
                    ),
                )
            ],
            (
                "<custodian>\n"
                "  <assignedCustodian>\n"
                "    <representedCustodianOrganization>\n"
                '      <id extension="112233"/>\n'
                "      <name>Happy Labs</name>\n"
                '      <telecom value="8888675309"/>\n'
                "      <addr>\n"
                "        <streetAddressLine>23 main st</streetAddressLine>\n"
                "        <streetAddressLine>apt 12</streetAddressLine>\n"
                "        <city>Fort Worth</city>\n"
                "        <state>Texas</state>\n"
                "        <postalCode>76006</postalCode>\n"
                "        <county>Tarrant</county>\n"
                "        <country>USA</country>\n"
                "      </addr>\n"
                "    </representedCustodianOrganization>\n"
                "  </assignedCustodian>\n"
                "</custodian>\n"
            ),
        ),
        # ValueError is raised when `id` is None
        (
            [Organization()],
            ValueError("The Custodian id parameter must be a defined."),
        ),
    ],
)
def test_build_custodian(build_custodian_test_data, expected_result):
    builder = PHDCBuilder()
    if isinstance(expected_result, ValueError):
        with pytest.raises(ValueError) as e:
            builder._build_custodian(build_custodian_test_data)
            assert str(e.value) == str(expected_result)

    else:
        xml_custodian_data = builder._build_custodian(build_custodian_test_data)
        assert (
            ET.tostring(xml_custodian_data, pretty_print=True).decode()
            == expected_result
        )


@patch.object(utils, "get_datetime_now", lambda: date(2010, 12, 15))
@pytest.mark.parametrize(
    "family_name, expected_oid, expected_date, expected_author",
    [
        # test for correct OID and name "CDC PRIME DIBBs"
        (
            "CDC PRIME DIBBs",
            "2.16.840.1.113883.19.5",
            "20101215000000",
            (
                '<author><time value="20101215000000"/><assignedAuthor><id root='
                + '"2.16.840.1.113883.19.5"/><assignedPerson><name><family>CDC PRIME '
                + "DIBBs</family></name></assignedPerson></assignedAuthor></author>"
            ),
        ),
        # test for correct OID and name "Local Health Jurisdiction"
        (
            "Local Health Jurisdiction",
            "2.16.840.1.113883.19.5",
            "20101215000000",
            (
                '<author><time value="20101215000000"/><assignedAuthor><id root="2.16.'
                + '840.1.113883.19.5"/><assignedPerson><name><family>Local Health '
                + "Jurisdiction</family></name></assignedPerson></assignedAuthor>"
                + "</author>"
            ),
        ),
    ],
)
def test_build_author(family_name, expected_oid, expected_date, expected_author):
    xml_author_data = PHDCBuilder()._build_author(family_name)
    author_string = ET.tostring(xml_author_data).decode()
    assert expected_oid in author_string
    assert expected_date in author_string
    assert expected_author in author_string
    assert expected_author == author_string


@pytest.mark.parametrize(
    "build_patient_test_data, expected_result",
    [
        # Success with all patient data
        (
            Patient(
                name=[
                    Name(prefix="Mr.", first="John", middle="Jacob", family="Schmidt")
                ],
                race_code="2106-3",
                ethnic_group_code="2186-5",
                administrative_gender_code="Male",
                birth_time="01-01-2000",
            ),
            (parse_file_from_test_assets("sample_phdc_patient_element.xml")),
        )
    ],
)
def test_build_patient(build_patient_test_data, expected_result):
    builder = PHDCBuilder()
    xml_patient_data = builder._build_patient(build_patient_test_data)
    formatter = formatting.DiffFormatter(
        normalize=formatting.WS_BOTH, pretty_print=True
    )
    diff = xmldiff.diff_trees(xml_patient_data, expected_result, formatter=formatter)

    assert diff == ""


@pytest.mark.parametrize(
    "build_rt_test_data, expected_result",
    [
        # Success with `id`
        (
            {
                "id": "TEST ID",
            },
            (
                "<recordTarget><patientRole>"
                + '<id extension="TEST ID"/>'
                + "</patientRole></recordTarget>"
            ),
        ),
        # ValueError is raised when `id` is None
        (
            {
                "id": None,
            },
            ValueError("The recordTarget id parameter must be a defined."),
        ),
    ],
)
def test_build_recordTarget(build_rt_test_data, expected_result):
    builder = PHDCBuilder()

    if isinstance(expected_result, ValueError):
        with pytest.raises(ValueError) as e:
            builder._build_recordTarget(**build_rt_test_data)
            assert str(e.value) == str(expected_result)

    else:
        xml_recordtarget_data = builder._build_recordTarget(**build_rt_test_data)
        assert ET.tostring(xml_recordtarget_data).decode() == expected_result


@patch.object(uuid, "uuid4", lambda: "mocked-uuid")
@patch.object(utils, "get_datetime_now", lambda: date(2010, 12, 15))
@pytest.mark.parametrize(
    "build_header_test_data, expected_result",
    [
        (
            PHDCInputData(
                organization=[Organization(id="112233")],
                patient=Patient(
                    name=[
                        Name(
                            prefix="Mr.",
                            first="John",
                            middle="Jacob",
                            family="Schmidt",
                            type="official",
                        ),
                        Name(
                            prefix="Mr.", first="JJ", family="Schmidt", type="pseudonym"
                        ),
                    ],
                    race_code="2106-3",
                    ethnic_group_code="2186-5",
                    administrative_gender_code="Male",
                    birth_time="01-01-2000",
                    telecom=[
                        Telecom(value="+1-800-555-1234"),
                        Telecom(value="+1-800-555-1234", type="work"),
                    ],
                    address=[
                        Address(
                            type="Home",
                            street_address_line_1="123 Main Street",
                            city="Brooklyn",
                            postal_code="11201",
                            state="New York",
                        ),
                        Address(
                            type="workplace",
                            street_address_line_1="123 Main Street",
                            postal_code="55866",
                            city="Brooklyn",
                            state="New York",
                        ),
                    ],
                ),
            ),
            (read_file_from_test_assets("sample_phdc_header.xml")),
        )
    ],
)
def test_build_header(build_header_test_data, expected_result):
    builder = PHDCBuilder()
    builder.set_input_data(build_header_test_data)
    builder.build_header()
    assert (
        ET.tostring(
            builder.phdc, pretty_print=True, xml_declaration=True, encoding="utf-8"
        ).decode("utf-8")
        == expected_result
    )


def test_build_base_phdc():
    builder = PHDCBuilder()
    base_phdc = builder._build_base_phdc()
    assert (
        ET.tostring(base_phdc)
        == b'<?xml-stylesheet type="text/xsl" href="PHDC.xsl"?><ClinicalDocument '
        b'xmlns="urn:hl7-org:v3" xmlns:sdt="urn:hl7-org:sdtc" '
        b'xmlns:sdtcxmlnamespaceholder="urn:hl7-org:v3" '
        b'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        b'xsi:schemaLocation="urn:hl7-org:v3 CDA_SDTC.xsd"/>'
    )


def test_get_type_id():
    builder = PHDCBuilder()
    type_id = builder._get_type_id()
    assert (
        ET.tostring(type_id)
        == b'<typeId root="2.16.840.1.113883.1.3" extension="POCD_HD000020"/>'
    )


@patch.object(uuid, "uuid4", lambda: "mocked-uuid")
def test_get_id():
    builder = PHDCBuilder()
    id = builder._get_id()
    assert (
        ET.tostring(id) == b'<id root="2.16.840.1.113883.19" extension="mocked-uuid"/>'
    )


def test_get_title():
    builder = PHDCBuilder()
    title = builder._get_title()

    assert (
        ET.tostring(title)
        == b"<title>Public Health Case Report - "
        + b"Data from the DIBBs FHIR to PHDC Converter</title>"
    )


@patch.object(utils, "get_datetime_now", lambda: date(2010, 12, 15))
def test_get_effective_time():
    builder = PHDCBuilder()
    effective_time = builder._get_effective_time()
    assert ET.tostring(effective_time) == b'<effectiveTime value="20101215000000"/>'


def test_get_confidentiality_code():
    builder = PHDCBuilder()
    confidentiality_code = builder._get_confidentiality_code(confidentiality="normal")
    assert (
        ET.tostring(confidentiality_code)
        == b'<confidentialityCode code="N" codeSystem="2.16.840.1.113883.5.25"/>'
    )


def test_get_setId():
    builder = PHDCBuilder()
    setid = builder._get_setId()

    assert ET.tostring(setid) == b'<setId extension="CLOSED_CASE" displayable="true"/>'


def test_get_version_number():
    builder = PHDCBuilder()
    version_number = builder._get_version_number()

    assert ET.tostring(version_number) == b'<versionNumber value="1"/>'


def test_get_realmCode():
    builder = PHDCBuilder()
    realmCode = builder._get_realmCode()
    assert ET.tostring(realmCode) == b'<realmCode code="US"/>'


def test_get_clinical_info_code():
    builder = PHDCBuilder()
    clinical_info_code = builder._get_clinical_info_code()
    assert (
        ET.tostring(clinical_info_code)
        == b'<code code="55751-2" codeSystem="2.16.840.1.113883.6.1" '
        b'codeSystemName="LOINC" displayName="Public Health Case Report - PHRI"/>'
    )


@patch.object(uuid, "uuid4", lambda: "mocked-uuid")
@pytest.mark.parametrize(
    "build_clinical_info_data, expected_result",
    [
        # Example test case
        (
            (
                PHDCInputData(
                    clinical_info=[
                        [
                            Observation(
                                type_code="COMP",
                                class_code="OBS",
                                mood_code="EVN",
                                code=CodedElement(
                                    code="INV169",
                                    code_system="2.16.840.1.114222.4.5.1",
                                    display_name="Condition",
                                ),
                                value=CodedElement(
                                    xsi_type="CE",
                                    code="10274",
                                    code_system="1.2.3.5",
                                    display_name="Chlamydia trachomatis infection",
                                ),
                                translation=CodedElement(
                                    xsi_type="CE",
                                    code="350",
                                    code_system="L",
                                    code_system_name="STD*MIS",
                                    display_name="Local Label",
                                ),
                            )
                        ],
                        [
                            Observation(
                                type_code="COMP",
                                class_code="OBS",
                                mood_code="EVN",
                                code=CodedElement(
                                    code="NBS012",
                                    code_system="2.16.840.1.114222.4.5.1",
                                    display_name="Shared Ind",
                                ),
                                value=CodedElement(
                                    xsi_type="CE",
                                    code="F",
                                    code_system="1.2.3.5",
                                    display_name="False",
                                ),
                                translation=CodedElement(
                                    xsi_type="CE",
                                    code="T",
                                    code_system="L",
                                    code_system_name="STD*MIS",
                                    display_name="Local Label",
                                ),
                            )
                        ],
                    ]
                )
            ),
            # Expected XML output as a string
            (
                '<component><section><id extension="mocked-uuid" assigningAuthorityName'
                + '="LR"/><code code="55752-0" codeSystem="2.16.840.1.113883.6.1" '
                + 'codeSystemName="LOINC" displayName="Clinical Information"/><title>'
                + 'Clinical Information</title><entry typeCode="COMP"><observation '
                + 'classCode="OBS" moodCode="EVN"><code code="INV169" codeSystem="2.16.'
                + '840.1.114222.4.5.1" displayName="Condition"/><value xsi:type="CE" '
                + 'code="10274" codeSystem="1.2.3.5" displayName="Chlamydia trachomatis'
                + ' infection"><translation xsi:type="CE" '
                + 'code="350" codeSystem="L" codeSystemName="STD*MIS" displayName='
                + '"Local '
                + 'Label"/></value></observation></entry><entry typeCode="COMP">'
                + '<observation classCode="OBS" moodCode="EVN"><code code="NBS012" '
                + 'codeSystem="2.16.840.1.114222.4.5.1" displayName="Shared Ind"/>'
                + "<value "
                + 'xsi:type="CE" code="F" codeSystem="1.2.3.5" displayName="False">'
                + "<transla"
                + 'tion xsi:type="CE" code="T" codeSystem="L" codeSystemName="STD*MIS" '
                + "disp"
                + 'layName="Local Label"/></value></observation></entry></section>'
                + "</component>"
            ),
        ),
    ],
)
def test_build_clinical_info(build_clinical_info_data, expected_result):
    builder = PHDCBuilder()
    builder.set_input_data(build_clinical_info_data)
    clinical_info_code = builder._build_clinical_info()
    actual_result = (
        ET.tostring(clinical_info_code)
        .decode()
        .replace('xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ', "")
    )
    assert actual_result == expected_result


@patch.object(uuid, "uuid4", lambda: "mocked-uuid")
@pytest.mark.parametrize(
    "build_social_history_info_data, expected_result",
    [
        # Example test case
        (
            (
                PHDCInputData(
                    social_history_info=[
                        [
                            Observation(
                                type_code="COMP",
                                class_code="OBS",
                                mood_code="EVN",
                                code=CodedElement(
                                    code="DEM127",
                                    code_system="2.16.840.1.114222.4.5.232",
                                    code_system_name="PHIN Questions",
                                    display_name="Is this person deceased?",
                                ),
                                value=CodedElement(
                                    xsi_type="CE",
                                    code="N",
                                    code_system_name="Yes/No Indicator (HL7)",
                                    display_name="No",
                                    code_system="2.16.840.1.113883.12.136",
                                ),
                                translation=CodedElement(
                                    code="N",
                                    code_system="2.16.840.1.113883.12.136",
                                    code_system_name="2.16.840.1.113883.12.136",
                                    display_name="No",
                                ),
                            )
                        ],
                        [
                            Observation(
                                type_code="COMP",
                                class_code="OBS",
                                mood_code="EVN",
                                code=CodedElement(
                                    code="NBS104",
                                    code_system="2.16.840.1.114222.4.5.1",
                                    code_system_name="NEDSS Base System",
                                    display_name="Information As of Date",
                                ),
                                value=CodedElement(
                                    xsi_type="TS",
                                    value="20240124",
                                ),
                            )
                        ],
                    ]
                )
            ),
            # Expected XML output as a string
            read_file_from_test_assets("sample_phdc_social_history_info.xml"),
        ),
    ],
)
def test_build_social_history_info(build_social_history_info_data, expected_result):
    builder = PHDCBuilder()
    builder.set_input_data(build_social_history_info_data)
    social_history_info = builder._build_social_history_info()
    assert (
        ET.tostring(
            social_history_info,
            pretty_print=True,
            xml_declaration=True,
            encoding="utf-8",
        ).decode("utf-8")
        == expected_result
    )


@patch.object(uuid, "uuid4", lambda: "mocked-uuid")
@patch.object(utils, "get_datetime_now", lambda: date(2010, 12, 15))
@pytest.mark.parametrize(
    "build_header_test_data, expected_result",
    [
        (
            PHDCInputData(
                type="case_report",
                patient=Patient(
                    name=[
                        Name(
                            prefix="Mr.",
                            first="John",
                            middle="Jacob",
                            family="Schmidt",
                            type="official",
                        ),
                        Name(
                            prefix="Mr.", first="JJ", family="Schmidt", type="pseudonym"
                        ),
                    ],
                    race_code="2106-3",
                    ethnic_group_code="2186-5",
                    administrative_gender_code="Male",
                    birth_time="01-01-2000",
                    telecom=[
                        Telecom(value="+1-800-555-1234"),
                        Telecom(value="+1-800-555-1234", type="work"),
                    ],
                    address=[
                        Address(
                            type="Home",
                            street_address_line_1="123 Main Street",
                            city="Brooklyn",
                            postal_code="11201",
                            state="New York",
                        ),
                        Address(
                            type="workplace",
                            street_address_line_1="123 Main Street",
                            postal_code="55866",
                            city="Brooklyn",
                            state="New York",
                        ),
                    ],
                ),
                clinical_info=[
                    [
                        Observation(
                            type_code="COMP",
                            class_code="OBS",
                            mood_code="EVN",
                            code=CodedElement(
                                code="INV169",
                                code_system="2.16.840.1.114222.4.5.1",
                                display_name="Condition",
                            ),
                            value=CodedElement(
                                xsi_type="CE",
                                code="10274",
                                code_system="1.2.3.5",
                                display_name="Chlamydia trachomatis infection",
                            ),
                            translation=CodedElement(
                                xsi_type="CE",
                                code="350",
                                code_system="L",
                                code_system_name="STD*MIS",
                                display_name="Local Label",
                            ),
                        )
                    ],
                    [
                        Observation(
                            type_code="COMP",
                            class_code="OBS",
                            mood_code="EVN",
                            code=CodedElement(
                                code="NBS012",
                                code_system="2.16.840.1.114222.4.5.1",
                                display_name="Shared Ind",
                            ),
                            value=CodedElement(
                                xsi_type="CE",
                                code="F",
                                code_system="1.2.3.5",
                                display_name="False",
                            ),
                            translation=CodedElement(
                                xsi_type="CE",
                                code="T",
                                code_system="L",
                                code_system_name="STD*MIS",
                                display_name="Local Label",
                            ),
                        )
                    ],
                ],
                social_history_info=[
                    [
                        Observation(
                            type_code="COMP",
                            class_code="OBS",
                            mood_code="EVN",
                            code=CodedElement(
                                code="DEM127",
                                code_system="2.16.840.1.114222.4.5.232",
                                code_system_name="PHIN Questions",
                                display_name="Is this person deceased?",
                            ),
                            value=CodedElement(
                                xsi_type="CE",
                                code="N",
                                code_system_name="Yes/No Indicator (HL7)",
                                display_name="No",
                                code_system="2.16.840.1.113883.12.136",
                            ),
                            translation=CodedElement(
                                code="N",
                                code_system="2.16.840.1.113883.12.136",
                                code_system_name="2.16.840.1.113883.12.136",
                                display_name="No",
                            ),
                        )
                    ],
                    [
                        Observation(
                            type_code="COMP",
                            class_code="OBS",
                            mood_code="EVN",
                            code=CodedElement(
                                code="NBS104",
                                code_system="2.16.840.1.114222.4.5.1",
                                code_system_name="NEDSS Base System",
                                display_name="Information As of Date",
                            ),
                            value=CodedElement(
                                xsi_type="TS",
                                value="20240124",
                            ),
                        )
                    ],
                ],
                repeating_questions=[
                    [
                        Observation(
                            obs_type="EXPOS",
                            type_code="COMP",
                            class_code="OBS",
                            mood_code="EVN",
                            code=CodedElement(
                                code="INV502",
                                code_system="2.16.840.1.113883.6.1",
                                code_system_name="LOINC",
                                display_name="Country of Exposure",
                            ),
                            value=CodedElement(
                                xsi_type="CE",
                                code="ATA",
                                code_system_name="Country (ISO 3166-1)",
                                display_name="ANTARCTICA",
                                code_system="1.0.3166.1",
                            ),
                        )
                    ],
                    [
                        Observation(
                            obs_type="EXPOS",
                            type_code="COMP",
                            class_code="OBS",
                            mood_code="EVN",
                            code=CodedElement(
                                code="INV504",
                                code_system="2.16.840.1.113883.6.1",
                                code_system_name="LOINC",
                                display_name="City of Exposure",
                            ),
                            value=CodedElement(
                                text="Esperanze",
                            ),
                        )
                    ],
                    [
                        Observation(
                            obs_type="EXPOS",
                            type_code="COMP",
                            class_code="OBS",
                            mood_code="EVN",
                            code=CodedElement(
                                code="INV502",
                                code_system="2.16.840.1.113883.6.1",
                                code_system_name="LOINC",
                                display_name="Country of Exposure",
                            ),
                            value=CodedElement(
                                xsi_type="CE",
                                code="ATA",
                                code_system_name="Country (ISO 3166-1)",
                                display_name="ANTARCTICA",
                                code_system="1.0.3166.1",
                            ),
                        ),
                        Observation(
                            obs_type="EXPOS",
                            type_code="COMP",
                            class_code="OBS",
                            mood_code="EVN",
                            code=CodedElement(
                                code="INV504",
                                code_system="2.16.840.1.113883.6.1",
                                code_system_name="LOINC",
                                display_name="City of Exposure",
                            ),
                            value=CodedElement(
                                text="Esperanze",
                            ),
                        ),
                    ],
                ],
                organization=[
                    Organization(
                        id="112233",
                        name="Happy Labs",
                        address=Address(
                            street_address_line_1="23 main st",
                            street_address_line_2="apt 12",
                            city="Fort Worth",
                            state="Texas",
                            postal_code="76006",
                            county="Tarrant",
                            country="USA",
                        ),
                        telecom=Telecom(value="8888675309"),
                    )
                ],
            ),
            read_file_from_test_assets("sample_phdc.xml"),
        )
    ],
)
def test_build(build_header_test_data, expected_result):
    builder = PHDCBuilder()
    builder.set_input_data(build_header_test_data)
    phdc = builder.build()
    actual_result = phdc.to_xml_string()
    assert actual_result == expected_result


def test_add_field():
    builder = PHDCBuilder()
    parent = ET.Element("parent")
    builder._add_field(parent, "test", "child")
    assert ET.tostring(parent) == b"<parent><child>test</child></parent>"


@pytest.mark.parametrize(
    "sort_observation_test_data, expected_result",
    [
        (
            Observation(
                type_code="COMP",
                class_code="OBS",
                mood_code="EVN",
                code_code="NBS012",
                code_code_system="2.16.840.1.114222.4.5.1",
                code_code_display="Shared Ind",
                value_quantitative_code=None,
                value_quant_code_system=None,
                value_quantitative_value=None,
                value_qualitative_code="F",
                value_qualitative_code_system="1.2.3.5",
                value_qualitative_value="False",
            ),
            Observation(
                type_code="COMP",
                class_code="OBS",
                mood_code="EVN",
                code=CodedElement(
                    xsi_type=None,
                    code="NBS012",
                    code_system="2.16.840.1.114222.4.5.1",
                    code_system_name=None,
                    display_name="Shared Ind",
                    value=None,
                ),
                value=CodedElement(
                    xsi_type=None,
                    code="F",
                    code_system="1.2.3.5",
                    code_system_name=None,
                    display_name=None,
                    value="False",
                ),
            ),
        )
    ],
)
def test_sort_observation(sort_observation_test_data, expected_result):
    builder = PHDCBuilder()
    builder.set_input_data(sort_observation_test_data)
    actual_result = builder._sort_observation(sort_observation_test_data)

    assert actual_result.code == expected_result.code
    assert actual_result.value == expected_result.value


@pytest.mark.parametrize(
    "build_repeating_questions_data, expected_result",
    [
        # Example test case
        (
            (
                PHDCInputData(
                    repeating_questions=[
                        [
                            Observation(
                                obs_type="EXPOS",
                                type_code="COMP",
                                class_code="OBS",
                                mood_code="EVN",
                                code=CodedElement(
                                    code="DEM127",
                                    code_system="2.16.840.1.114222.4.5.232",
                                    code_system_name="PHIN Questions",
                                    display_name="Is this person deceased?",
                                ),
                                value=CodedElement(
                                    xsi_type="CE",
                                    code="N",
                                    code_system_name="Yes/No Indicator (HL7)",
                                    display_name="No",
                                    code_system="2.16.840.1.113883.12.136",
                                ),
                                translation=CodedElement(
                                    code="N",
                                    code_system="2.16.840.1.113883.12.136",
                                    code_system_name="2.16.840.1.113883.12.136",
                                    display_name="No",
                                ),
                            )
                        ],
                        [
                            Observation(
                                obs_type="EXPOS",
                                type_code="COMP",
                                class_code="OBS",
                                mood_code="EVN",
                                code=CodedElement(
                                    code="NBS104",
                                    code_system="2.16.840.1.114222.4.5.1",
                                    code_system_name="NEDSS Base System",
                                    display_name="Information As of Date",
                                ),
                                value=CodedElement(
                                    xsi_type="TS",
                                    value="20240124",
                                ),
                            )
                        ],
                        [
                            Observation(
                                obs_type="EXPOS",
                                type_code="COMP",
                                class_code="OBS",
                                mood_code="EVN",
                                code=CodedElement(
                                    code="DEM127",
                                    code_system="List Item 1",
                                    code_system_name="PHIN Questions",
                                    display_name="Is this person deceased?",
                                ),
                                value=CodedElement(
                                    xsi_type="CE",
                                    code="N",
                                    code_system_name="List Item 1",
                                    display_name="List Item 1",
                                    code_system="2.16.840.1.113883.12.136",
                                ),
                            ),
                            Observation(
                                obs_type="EXPOS",
                                type_code="COMP",
                                class_code="OBS",
                                mood_code="EVN",
                                code=CodedElement(
                                    code="NBS104",
                                    code_system="2.16.840.1.114222.4.5.1",
                                    code_system_name="NEDSS Base System",
                                    display_name="List Item 2",
                                ),
                                value=CodedElement(
                                    xsi_type="TS",
                                    value="List Item 2",
                                ),
                            ),
                        ],
                    ]
                )
            ),
            # Expected XML output as a string
            read_file_from_test_assets("sample_phdc_repeating_questions.xml"),
        ),
    ],
)
def test_build_repeating_questions(build_repeating_questions_data, expected_result):
    builder = PHDCBuilder()
    builder.set_input_data(build_repeating_questions_data)
    repeating_questions = builder._build_repeating_questions()
    assert (
        ET.tostring(
            repeating_questions,
            pretty_print=True,
            xml_declaration=True,
            encoding="utf-8",
        ).decode("utf-8")
        == expected_result
    )


def test_translate_code_system():
    input_data = Observation(
        obs_type="EXPOS",
        type_code="COMP",
        class_code="OBS",
        mood_code="EVN",
        code_system="http://snomed.info/sct",
        code_code="1234",
        code_code_system="http://loinc.org",
        value_quant_code_system="http://acme-rehab.org",
        value_qualitative_code_system="2.16.840.1.114222.4.5.1",
    )

    expected_result = Observation(
        obs_type="EXPOS",
        type_code="COMP",
        class_code="OBS",
        code_display=None,
        code_system="2.16.840.1.113883.6.96",
        code_system_name="SNOMED-CT",
        quantitative_value=None,
        quantitative_system=None,
        quantitative_code=None,
        qualitative_value=None,
        qualitative_system=None,
        qualitative_code=None,
        mood_code="EVN",
        code_code="1234",
        code_code_system="number",
        code_code_system_name="LOINC",
        code_code_display=None,
        value_quantitative_code=None,
        value_quant_code_system="Acme Rehab",
        value_quant_code_system_name="Acme Rehab",
        value_quantitative_value=None,
        value_qualitative_code=None,
        value_qualitative_code_system="2.16.840.1.114222.4.5.1",
        value_qualitative_code_system_name="NEDSS Base System",
        value_qualitative_value=None,
        components=None,
        code=None,
        value=None,
        translation=None,
        text=None,
    )
    builder = PHDCBuilder()
    actual_result = builder._translate_code_system(input_data)
    assert actual_result == expected_result
