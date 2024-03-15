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
                    xsi_type="CE", code="2", code_system="1", display_name="V"
                ),
            ),
            (
                '<observation classCode="OBS" moodCode="EVN"><code code="1" '
                + 'codeSystem="0" displayName="Code"/><value xsi:type="CE" code="2" '
                + 'codeSystem="1" displayName="V"/></observation>'
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
                    Name(
                        prefix="Ms.",
                        first="Saga",
                        middle=None,
                        family="Anderson",
                        type="official",
                    ),
                ],
                race_code="2054-5",
                ethnic_group_code="2186-5",
                administrative_gender_code="female",
                birth_time="1987-11-11",
            ),
            (parse_file_from_test_assets("sample_valid_phdc_response.xml")),
        )
    ],
)
def test_build_patient(build_patient_test_data, expected_result):
    builder = PHDCBuilder()
    actual_result = builder._build_patient(build_patient_test_data)

    actual_result = (
        ET.tostring(actual_result, xml_declaration=True, pretty_print=True)
        .decode()
        .replace(' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"', "")
        .replace(' xmlns:sdt="urn:hl7-org:sdtc"', "")
    )

    header = expected_result.getroot()
    for elem in header.getiterator():
        if "race" in elem.tag:
            continue
        elem.tag = ET.QName(elem).localname
    ET.cleanup_namespaces(header)

    # Remove components
    for component in header.findall("component"):
        header.remove(component)

    for c in header:
        if c.tag == "recordTarget":
            for elem in c:
                if elem.tag == "patientRole":
                    for item in elem:
                        if item.tag == "patient":
                            expected_result = item

    expected_result = (
        ET.tostring(expected_result, xml_declaration=True, pretty_print=True)
        .decode()
        .replace(' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"', "")
        .replace(' xmlns:sdt="urn:hl7-org:sdtc"', "")
    )
    assert actual_result == expected_result


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


@patch.object(uuid, "uuid4", lambda: "495669c7-96bf-4573-9dd8-59e745e05576")
@patch.object(utils, "get_datetime_now", lambda: date(2010, 12, 15))
@pytest.mark.parametrize(
    "build_header_test_data, expected_result",
    [
        (
            PHDCInputData(
                organization=[
                    Organization(
                        id="495669c7-96bf-4573-9dd8-59e745e05576",
                        name="Nelson Family Practice",
                        telecom=Telecom(value="206-555-0199"),
                        address=Address(
                            street_address_line_1="123 Harbor St",
                            street_address_line_2=None,
                            city="Bright Falls",
                            state="WA",
                            postal_code="98440",
                            county=None,
                            country="United States",
                        ),
                    )
                ],
                patient=Patient(
                    name=[
                        Name(
                            prefix="Ms.",
                            first="Saga",
                            middle=None,
                            family="Anderson",
                            type="official",
                        ),
                    ],
                    race_code="2054-5",
                    ethnic_group_code="2186-5",
                    administrative_gender_code="female",
                    birth_time="1987-11-11",
                    telecom=None,
                    address=[
                        Address(
                            type="Home",
                            street_address_line_1="6 Watery Lighthouse"
                            + " Trailer Park Way",
                            street_address_line_2="Unit #2",
                            city="Watery",
                            state="WA",
                            postal_code="98440",
                            country="United States",
                        )
                    ],
                ),
            ),
            (parse_file_from_test_assets("sample_valid_phdc_response.xml")),
        )
    ],
)
def test_build_header(build_header_test_data, expected_result):
    builder = PHDCBuilder()
    builder.set_input_data(build_header_test_data)
    builder.build_header()
    header_tree = builder.phdc
    actual_header = header_tree.getroot()
    for elem in actual_header.getiterator():
        elem.tag = ET.QName(elem).localname
    ET.cleanup_namespaces(actual_header)
    expected_header = utils.get_phdc_section("header", expected_result)

    actual_flattened = [i.tag for i in actual_header.iter()]
    expected_flattened = [i.tag for i in expected_header.iter()]

    assert actual_flattened == expected_flattened


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


@patch.object(uuid, "uuid4", lambda: "495669c7-96bf-4573-9dd8-59e745e05576")
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
                                    code="INV163",
                                    code_system="2.16.840.1.114222.4.5.232",
                                    code_system_name="PHIN Questions",
                                    display_name="Case Status",
                                ),
                                value=CodedElement(
                                    xsi_type="CE",
                                    code="410605003",
                                    code_system="2.16.840.1.113883.6.96",
                                    display_name="Confirmed",
                                ),
                            )
                        ],
                        [
                            Observation(
                                type_code="COMP",
                                class_code="OBS",
                                mood_code="EVN",
                                code=CodedElement(
                                    code="INV169",
                                    code_system="2.16.840.1.114222.4.5.232",
                                    code_system_name="PHIN Questions",
                                    display_name="Condition",
                                ),
                                value=CodedElement(
                                    xsi_type="CE",
                                    code="10110",
                                    code_system="2.16.840.1.114222.4.5.277",
                                    code_system_name="Notifiable Event Code List",
                                    display_name="Hepatitis A, acute",
                                ),
                            )
                        ],
                        [
                            Observation(
                                type_code="COMP",
                                class_code="OBS",
                                mood_code="EVN",
                                code=CodedElement(
                                    code="INV163",
                                    code_system="2.16.840.1.114222.4.5.232",
                                    code_system_name="PHIN Questions",
                                    display_name="Case Status",
                                ),
                                value=CodedElement(
                                    xsi_type="CE",
                                    code="410605003",
                                    code_system="2.16.840.1.113883.6.96",
                                    display_name="Confirmed",
                                ),
                            )
                        ],
                        [
                            Observation(
                                type_code="COMP",
                                class_code="OBS",
                                mood_code="EVN",
                                code=CodedElement(
                                    code="INV169",
                                    code_system="2.16.840.1.114222.4.5.232",
                                    code_system_name="PHIN Questions",
                                    display_name="Condition",
                                ),
                                value=CodedElement(
                                    xsi_type="CE",
                                    code="10110",
                                    code_system="2.16.840.1.114222.4.5.277",
                                    code_system_name="Notifiable Event Code List",
                                    display_name="Hepatitis A, acute",
                                ),
                            )
                        ],
                        [
                            Observation(
                                type_code="COMP",
                                class_code="OBS",
                                mood_code="EVN",
                                code=CodedElement(
                                    code="NBS055",
                                    code_system="2.16.840.1.114222.4.5.1",
                                    code_system_name="NEDSS Base System",
                                    display_name="Contact Investigation Priority",
                                ),
                                value=CodedElement(
                                    xsi_type="CE",
                                    code="LOW",
                                    code_system="L",
                                    display_name="Low",
                                ),
                            )
                        ],
                        [
                            Observation(
                                type_code="COMP",
                                class_code="OBS",
                                mood_code="EVN",
                                code=CodedElement(
                                    code="NBS058",
                                    code_system="2.16.840.1.114222.4.5.1",
                                    code_system_name="NEDSS Base System",
                                    display_name="Contact Investigation Status",
                                ),
                                value=CodedElement(
                                    xsi_type="CE",
                                    code="385651009",
                                    code_system="2.16.840.1.113883.6.96",
                                    display_name="In progress",
                                ),
                            )
                        ],
                        [
                            Observation(
                                type_code="COMP",
                                class_code="OBS",
                                mood_code="EVN",
                                code=CodedElement(
                                    code="INV148",
                                    code_system="2.16.840.1.114222.4.5.232",
                                    code_system_name="PHIN Questions",
                                    display_name="Is this person associated with a day"
                                    + " care facility?",
                                ),
                                value=CodedElement(
                                    xsi_type="CE",
                                    code="Y",
                                    code_system="2.16.840.1.113883.12.136",
                                    display_name="Yes",
                                ),
                            )
                        ],
                    ]
                )
            ),
            # Expected XML output
            (parse_file_from_test_assets("sample_valid_phdc_response.xml")),
        ),
    ],
)
def test_build_clinical_info(build_clinical_info_data, expected_result):
    builder = PHDCBuilder()
    builder.set_input_data(build_clinical_info_data)
    clinical_info_code = builder._build_clinical_info()
    actual_result = (
        ET.tostring(clinical_info_code, pretty_print=True)
        .decode()
        .replace(' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"', "")
    )

    expected_result = utils.get_phdc_section("Clinical Information", expected_result)
    expected_result = (
        ET.tostring(expected_result, pretty_print=True)
        .decode()
        .replace(' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"', "")
    )

    assert actual_result == expected_result


@patch.object(uuid, "uuid4", lambda: "495669c7-96bf-4573-9dd8-59e745e05576")
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
                                    # code_system_name="Yes/No Indicator (HL7)",
                                    display_name="No",
                                    code_system="2.16.840.1.113883.12.136",
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
                        [
                            Observation(
                                type_code="COMP",
                                class_code="OBS",
                                mood_code="EVN",
                                code=CodedElement(
                                    code="INV2001",
                                    code_system="2.16.840.1.114222.4.5.232",
                                    code_system_name="PHIN Questions",
                                    display_name="Reported Age",
                                ),
                                value=CodedElement(
                                    xsi_type="ST",
                                    text="36",
                                ),
                            )
                        ],
                        [
                            Observation(
                                type_code="COMP",
                                class_code="OBS",
                                mood_code="EVN",
                                code=CodedElement(
                                    code="INV2002",
                                    code_system="2.16.840.1.114222.4.5.232",
                                    code_system_name="PHIN Questions",
                                    display_name="Reported Age Units",
                                ),
                                value=CodedElement(
                                    xsi_type="CE",
                                    code="a",
                                    code_system="2.16.840.1.113883.6.8",
                                    display_name="year [time]",
                                ),
                            )
                        ],
                    ]
                )
            ),
            # Expected XML output as a string
            parse_file_from_test_assets("sample_valid_phdc_response.xml"),
        ),
    ],
)
def test_build_social_history_info(build_social_history_info_data, expected_result):
    builder = PHDCBuilder()
    builder.set_input_data(build_social_history_info_data)
    actual_result = builder._build_social_history_info()
    actual_result = (
        ET.tostring(actual_result, pretty_print=True)
        .decode()
        .replace(' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"', "")
    )

    expected_result = utils.get_phdc_section(
        "SOCIAL HISTORY INFORMATION", expected_result
    )
    expected_result = (
        ET.tostring(expected_result, pretty_print=True)
        .decode()
        .replace(' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"', "")
    )
    assert actual_result == expected_result


@patch.object(uuid, "uuid4", lambda: "495669c7-96bf-4573-9dd8-59e745e05576")
@patch.object(utils, "get_datetime_now", lambda: date(2010, 12, 15))
@pytest.mark.parametrize(
    "build_test_data, expected_result",
    [
        (
            PHDCInputData(
                type="case_report",
                patient=Patient(
                    name=[
                        Name(
                            prefix="Ms.",
                            first="Saga",
                            middle=None,
                            family="Anderson",
                            type="official",
                        ),
                    ],
                    race_code="2054-5",
                    ethnic_group_code="2186-5",
                    administrative_gender_code="female",
                    birth_time="1987-11-11",
                    telecom=None,
                    address=[
                        Address(
                            type="Home",
                            street_address_line_1="6 Watery Lighthouse Trailer"
                            + " Park Way",
                            street_address_line_2="Unit #2",
                            city="Watery",
                            state="WA",
                            postal_code="98440",
                            country="United States",
                        )
                    ],
                ),
                clinical_info=[
                    [
                        Observation(
                            type_code="COMP",
                            class_code="OBS",
                            mood_code="EVN",
                            code=CodedElement(
                                code="INV163",
                                code_system="2.16.840.1.114222.4.5.232",
                                code_system_name="PHIN Questions",
                                display_name="Case Status",
                            ),
                            value=CodedElement(
                                xsi_type="CE",
                                code="410605003",
                                code_system="2.16.840.1.113883.6.96",
                                display_name="Confirmed",
                            ),
                        )
                    ],
                    [
                        Observation(
                            type_code="COMP",
                            class_code="OBS",
                            mood_code="EVN",
                            code=CodedElement(
                                code="INV169",
                                code_system="2.16.840.1.114222.4.5.232",
                                code_system_name="PHIN Questions",
                                display_name="Condition",
                            ),
                            value=CodedElement(
                                xsi_type="CE",
                                code="10110",
                                code_system="2.16.840.1.114222.4.5.277",
                                code_system_name="Notifiable Event Code List",
                                display_name="Hepatitis A, acute",
                            ),
                        )
                    ],
                    [
                        Observation(
                            type_code="COMP",
                            class_code="OBS",
                            mood_code="EVN",
                            code=CodedElement(
                                code="INV163",
                                code_system="2.16.840.1.114222.4.5.232",
                                code_system_name="PHIN Questions",
                                display_name="Case Status",
                            ),
                            value=CodedElement(
                                xsi_type="CE",
                                code="410605003",
                                code_system="2.16.840.1.113883.6.96",
                                display_name="Confirmed",
                            ),
                        )
                    ],
                    [
                        Observation(
                            type_code="COMP",
                            class_code="OBS",
                            mood_code="EVN",
                            code=CodedElement(
                                code="INV169",
                                code_system="2.16.840.1.114222.4.5.232",
                                code_system_name="PHIN Questions",
                                display_name="Condition",
                            ),
                            value=CodedElement(
                                xsi_type="CE",
                                code="10110",
                                code_system="2.16.840.1.114222.4.5.277",
                                code_system_name="Notifiable Event Code List",
                                display_name="Hepatitis A, acute",
                            ),
                        )
                    ],
                    [
                        Observation(
                            type_code="COMP",
                            class_code="OBS",
                            mood_code="EVN",
                            code=CodedElement(
                                code="NBS055",
                                code_system="2.16.840.1.114222.4.5.1",
                                code_system_name="NEDSS Base System",
                                display_name="Contact Investigation Priority",
                            ),
                            value=CodedElement(
                                xsi_type="CE",
                                code="LOW",
                                code_system="L",
                                display_name="Low",
                            ),
                        )
                    ],
                    [
                        Observation(
                            type_code="COMP",
                            class_code="OBS",
                            mood_code="EVN",
                            code=CodedElement(
                                code="NBS058",
                                code_system="2.16.840.1.114222.4.5.1",
                                code_system_name="NEDSS Base System",
                                display_name="Contact Investigation Status",
                            ),
                            value=CodedElement(
                                xsi_type="CE",
                                code="385651009",
                                code_system="2.16.840.1.113883.6.96",
                                display_name="In progress",
                            ),
                        )
                    ],
                    [
                        Observation(
                            type_code="COMP",
                            class_code="OBS",
                            mood_code="EVN",
                            code=CodedElement(
                                code="INV148",
                                code_system="2.16.840.1.114222.4.5.232",
                                code_system_name="PHIN Questions",
                                display_name="Is this person associated with a"
                                + " day care facility?",
                            ),
                            value=CodedElement(
                                xsi_type="CE",
                                code="Y",
                                code_system="2.16.840.1.113883.12.136",
                                display_name="Yes",
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
                                # code_system_name="Yes/No Indicator (HL7)",
                                display_name="No",
                                code_system="2.16.840.1.113883.12.136",
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
                    [
                        Observation(
                            type_code="COMP",
                            class_code="OBS",
                            mood_code="EVN",
                            code=CodedElement(
                                code="INV2001",
                                code_system="2.16.840.1.114222.4.5.232",
                                code_system_name="PHIN Questions",
                                display_name="Reported Age",
                            ),
                            value=CodedElement(
                                xsi_type="ST",
                                text="36",
                            ),
                        )
                    ],
                    [
                        Observation(
                            type_code="COMP",
                            class_code="OBS",
                            mood_code="EVN",
                            code=CodedElement(
                                code="INV2002",
                                code_system="2.16.840.1.114222.4.5.232",
                                code_system_name="PHIN Questions",
                                display_name="Reported Age Units",
                            ),
                            value=CodedElement(
                                xsi_type="CE",
                                code="a",
                                code_system="2.16.840.1.113883.6.8",
                                display_name="year [time]",
                            ),
                        )
                    ],
                ],
                repeating_questions=[
                    [
                        Observation(
                            obs_type="EXPOS",
                            type_code=None,
                            class_code=None,
                            code_display=None,
                            code_system=None,
                            code_system_name=None,
                            quantitative_value=None,
                            quantitative_system=None,
                            quantitative_code=None,
                            qualitative_value=None,
                            qualitative_system=None,
                            qualitative_code=None,
                            mood_code=None,
                            code_code="69730-0",
                            code_code_system="http://loinc.org",
                            code_code_system_name=None,
                            code_code_display="Questionnaire Document",
                            value_quantitative_code=None,
                            value_quant_code_system=None,
                            value_quant_code_system_name=None,
                            value_quantitative_value=None,
                            value_qualitative_code=None,
                            value_qualitative_code_system=None,
                            value_qualitative_code_system_name=None,
                            value_qualitative_value=None,
                            components=[
                                {
                                    "code_code": "INV502",
                                    "code_code_display": "Country of Exposure",
                                    "code_code_system": "2.16.840.1.113883.6.1",
                                    "text": None,
                                    "value_qualitative_code": "USA",
                                    "value_qualitative_code_system": "1.0.3166.1",
                                    "value_qualitative_value": "UNITED STATES",
                                    "value_quant_code_system": None,
                                    "value_quantitative_code": None,
                                    "value_quantitative_value": None,
                                },
                                {
                                    "code_code": "INV503",
                                    "code_code_display": "State or Province"
                                    + " of Exposure",
                                    "code_code_system": "2.16.840.1.113883.6.1",
                                    "text": None,
                                    "value_qualitative_code": "53",
                                    "value_qualitative_code_system": "2.16.840.1."
                                    + "113883.6.92",
                                    "value_qualitative_value": "Washington",
                                    "value_quant_code_system": None,
                                    "value_quantitative_code": None,
                                    "value_quantitative_value": None,
                                },
                                {
                                    "code_code": "INV504",
                                    "code_code_display": "City of Exposure",
                                    "code_code_system": "2.16.840.1.113883.6.1",
                                    "text": None,
                                    "value_qualitative_code": None,
                                    "value_qualitative_code_system": None,
                                    "value_qualitative_value": "Bright Falls",
                                    "value_quant_code_system": None,
                                    "value_quantitative_code": None,
                                    "value_quantitative_value": None,
                                },
                                {
                                    "code_code": "INV505",
                                    "code_code_display": "County of Exposure",
                                    "code_code_system": "2.16.840.1.113883.6.1",
                                    "text": None,
                                    "value_qualitative_code": "053",
                                    "value_qualitative_code_system": "2.16.840.1."
                                    + "113883.6.93",
                                    "value_qualitative_value": "Pierce County",
                                    "value_quant_code_system": None,
                                    "value_quantitative_code": None,
                                    "value_quantitative_value": None,
                                },
                            ],
                            code=None,
                            value=None,
                            translation=None,
                            text=None,
                        )
                    ]
                ],
                organization=[
                    Organization(
                        id="495669c7-96bf-4573-9dd8-59e745e05576",
                        name="Nelson Family Practice",
                        telecom=Telecom(value="206-555-0199"),
                        address=Address(
                            street_address_line_1="123 Harbor St",
                            street_address_line_2=None,
                            city="Bright Falls",
                            state="WA",
                            postal_code="98440",
                            county=None,
                            country="United States",
                        ),
                    )
                ],
            ),
            parse_file_from_test_assets("sample_valid_phdc_response.xml"),
        )
    ],
)
def test_build(build_test_data, expected_result):
    builder = PHDCBuilder()
    builder.set_input_data(build_test_data)
    phdc = builder.build()
    actual_result = (
        ET.tostring(
            phdc.data, pretty_print=True, xml_declaration=True, encoding="utf-8"
        )
        .decode()
        .replace(' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"', "")
    )

    expected_result = (
        ET.tostring(
            expected_result, pretty_print=True, xml_declaration=True, encoding="utf-8"
        )
        .decode()
        .replace(' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"', "")
    )

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
    "set_xsi_test_data, expected_result",
    [
        # test that CE works as expected and that the
        # code.xsi_type will get set to None
        (
            Observation(
                type_code="COMP",
                class_code="OBS",
                mood_code="EVN",
                code=CodedElement(
                    xsi_type="CE",
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
                    xsi_type="CE",
                    code="F",
                    code_system="1.2.3.5",
                    code_system_name=None,
                    display_name=None,
                    value="False",
                ),
            ),
        ),
        # test that ST works as expected
        (
            Observation(
                type_code="COMP",
                class_code="OBS",
                mood_code="EVN",
                code=CodedElement(
                    xsi_type=None,
                    code="INV504",
                    code_system=None,
                    code_system_name="LocalSystem",
                    display_name="City of Exposure",
                    value=None,
                ),
                value=CodedElement(
                    xsi_type=None,
                    code=None,
                    code_system=None,
                    code_system_name=None,
                    display_name="State",
                    value="Atlanta",
                ),
            ),
            Observation(
                type_code="COMP",
                class_code="OBS",
                mood_code="EVN",
                code=CodedElement(
                    xsi_type=None,
                    code="INV504",
                    code_system=None,
                    code_system_name="LocalSystem",
                    display_name="City of Exposure",
                    value=None,
                ),
                value=CodedElement(
                    xsi_type="ST",
                    code=None,
                    code_system=None,
                    code_system_name=None,
                    display_name=None,
                    value=None,
                    text="Atlanta",
                ),
            ),
        ),
        # test that TS works as expected
        (
            Observation(
                type_code="COMP",
                class_code="OBS",
                mood_code="EVN",
                code=CodedElement(
                    xsi_type=None,
                    code="NBS104",
                    code_system="2.16.840.1.114222.4.5.1",
                    code_system_name="NEDSS Base System",
                    display_name="Information As of Date",
                    value=None,
                ),
                value=CodedElement(
                    xsi_type=None,
                    code=None,
                    code_system=None,
                    code_system_name=None,
                    display_name=None,
                    value="2024-01-24",
                ),
            ),
            Observation(
                type_code="COMP",
                class_code="OBS",
                mood_code="EVN",
                code=CodedElement(
                    xsi_type=None,
                    code="NBS104",
                    code_system="2.16.840.1.114222.4.5.1",
                    code_system_name="NEDSS Base System",
                    display_name="Information As of Date",
                    value=None,
                ),
                value=CodedElement(
                    xsi_type="TS",
                    code=None,
                    code_system=None,
                    code_system_name=None,
                    display_name=None,
                    value="20240124",
                ),
            ),
        ),
    ],
)
def test_set_value_xsi_type(set_xsi_test_data, expected_result):
    builder = PHDCBuilder()
    builder.set_input_data(set_xsi_test_data)
    actual_result = builder._set_value_xsi_type(set_xsi_test_data)

    assert actual_result.code.xsi_type == expected_result.code.xsi_type
    assert actual_result.value.xsi_type == expected_result.value.xsi_type
    if actual_result.value.xsi_type == "ST":
        assert actual_result.value.text == expected_result.value.text
    if actual_result.value.xsi_type == "TS":
        assert actual_result.value.value == expected_result.value.value


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
                                type_code=None,
                                class_code=None,
                                code_display=None,
                                code_system=None,
                                code_system_name=None,
                                quantitative_value=None,
                                quantitative_system=None,
                                quantitative_code=None,
                                qualitative_value=None,
                                qualitative_system=None,
                                qualitative_code=None,
                                mood_code=None,
                                code_code="69730-0",
                                code_code_system="http://loinc.org",
                                code_code_system_name=None,
                                code_code_display="Questionnaire Document",
                                value_quantitative_code=None,
                                value_quant_code_system=None,
                                value_quant_code_system_name=None,
                                value_quantitative_value=None,
                                value_qualitative_code=None,
                                value_qualitative_code_system=None,
                                value_qualitative_code_system_name=None,
                                value_qualitative_value=None,
                                components=[
                                    {
                                        "code_code": "INV502",
                                        "code_code_display": "Country of Exposure",
                                        "code_code_system": "2.16.840.1.113883.6.1",
                                        "text": None,
                                        "value_qualitative_code": "USA",
                                        "value_qualitative_code_system": "1.0.3166.1",
                                        "value_qualitative_value": "UNITED STATES",
                                        "value_quant_code_system": None,
                                        "value_quantitative_code": None,
                                        "value_quantitative_value": None,
                                    },
                                    {
                                        "code_code": "INV503",
                                        "code_code_display": "State or Province"
                                        + " of Exposure",
                                        "code_code_system": "2.16.840.1.113883.6.1",
                                        "text": None,
                                        "value_qualitative_code": "53",
                                        "value_qualitative_code_system": "2.16.840.1."
                                        + "113883.6.92",
                                        "value_qualitative_value": "Washington",
                                        "value_quant_code_system": None,
                                        "value_quantitative_code": None,
                                        "value_quantitative_value": None,
                                    },
                                    {
                                        "code_code": "INV504",
                                        "code_code_display": "City of Exposure",
                                        "code_code_system": "2.16.840.1.113883.6.1",
                                        "text": None,
                                        "value_qualitative_code": None,
                                        "value_qualitative_code_system": None,
                                        "value_qualitative_value": "Bright Falls",
                                        "value_quant_code_system": None,
                                        "value_quantitative_code": None,
                                        "value_quantitative_value": None,
                                    },
                                    {
                                        "code_code": "INV505",
                                        "code_code_display": "County of Exposure",
                                        "code_code_system": "2.16.840.1.113883.6.1",
                                        "text": None,
                                        "value_qualitative_code": "053",
                                        "value_qualitative_code_system": "2.16.840.1."
                                        + "113883.6.93",
                                        "value_qualitative_value": "Pierce County",
                                        "value_quant_code_system": None,
                                        "value_quantitative_code": None,
                                        "value_quantitative_value": None,
                                    },
                                ],
                                code=None,
                                value=None,
                                translation=None,
                                text=None,
                            )
                        ]
                    ]
                )
            ),
            # Expected XML output as a string
            parse_file_from_test_assets("sample_valid_phdc_response.xml"),
        ),
    ],
)
def test_build_repeating_questions(build_repeating_questions_data, expected_result):
    builder = PHDCBuilder()
    builder.set_input_data(build_repeating_questions_data)
    actual_result = builder._build_repeating_questions()
    actual_result = (
        ET.tostring(actual_result, pretty_print=True)
        .decode()
        .replace(' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"', "")
    )

    expected_result = utils.get_phdc_section("REPEATING QUESTIONS", expected_result)
    expected_result = (
        ET.tostring(expected_result, pretty_print=True)
        .decode()
        .replace(' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"', "")
    )
    assert actual_result == expected_result


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
