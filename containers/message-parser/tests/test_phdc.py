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
from app.phdc.models import Patient
from app.phdc.models import PHDCInputData
from app.phdc.models import Telecom
from lxml import etree as ET


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
    "build_observation_test_data, expected_result",
    [
        # Test case with a single code element, value, and translation
        (
            Observation(
                type_code="ENTRY",
                class_code="OBS",
                mood_code="EVN",
                code=[CodedElement(code="1", code_system="0", display_name="Code")],
                value=[
                    CodedElement(
                        xsi_type="ST", code="2", code_system="1", display_name="V"
                    )
                ],
                translation=[
                    CodedElement(
                        xsi_type="T", code="0", code_system="L", display_name="T"
                    )
                ],
            ),
            (
                '<entry typeCode="ENTRY">'
                + '<observation classCode="OBS" moodCode="EVN">'
                + '<code code="1" codeSystem="0" displayName="Code"/>'
                + '<value xsi:type="ST" code="2" codeSystem="1" displayName="V">'
                + '<translation xsi:type="T" code="0" codeSystem="L" displayName="T"/>'
                + "</value></observation></entry>"
            ),
        )
    ],
)
def test_build_observation(build_observation_test_data, expected_result):
    builder = PHDCBuilder()
    # TODO: is there a better way to acknowledge xsi:type requires xmlns that is
    # established earlier in the clinicaldocument portion?
    with pytest.raises(ValueError, match="Invalid attribute name 'xsi:type'"):
        xod = builder._build_observation_method(build_observation_test_data)
        actual_result = ET.tostring(xod, encoding="unicode")
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
        # Success with `id`
        (
            {
                "id": "TEST ID",
            },
            (
                "<custodian><assignedCustodian><representedCustodianOrganization>"
                + '<id extension="TEST ID"/></representedCustodianOrganization>'
                + "</assignedCustodian></custodian>"
            ),
        ),
        # ValueError is raised when `id` is None
        (
            {
                "id": None,
            },
            ValueError("The Custodian id parameter must be a defined."),
        ),
    ],
)
def test_build_custodian(build_custodian_test_data, expected_result):
    builder = PHDCBuilder()
    if isinstance(expected_result, ValueError):
        with pytest.raises(ValueError) as e:
            xml_custodian_data = builder._build_custodian(**build_custodian_test_data)
            assert str(e.value) == str(expected_result)

    else:
        xml_custodian_data = builder._build_custodian(**build_custodian_test_data)
        assert ET.tostring(xml_custodian_data).decode() == expected_result


@patch.object(utils, "get_datetime_now", lambda: date(2010, 12, 15))
@pytest.mark.parametrize(
    "family_name, expected_oid, expected_date, expected_name",
    [
        # test for correct OID and name "CDC PRIME DIBBs"
        (
            "CDC PRIME DIBBs",
            "2.16.840.1.113883.19.5",
            "20101215000000",
            (
                '<author><time value="20101215000000"/><assignedAuthor>'
                '<id root="2.16.840.1.113883.19.5"/><name>'
                "<family>CDC PRIME DIBBs</family></name>"
                "</assignedAuthor></author>"
            ),
        ),
        # test for correct OID and name "Local Health Jurisdiction"
        (
            "Local Health Jurisdiction",
            "2.16.840.1.113883.19.5",
            "20101215000000",
            (
                '<author><time value="20101215000000"/><assignedAuthor>'
                '<id root="2.16.840.1.113883.19.5"/><name>'
                "<family>Local Health Jurisdiction</family></name>"
                "</assignedAuthor></author>"
            ),
        ),
    ],
)
def test_build_author(family_name, expected_oid, expected_date, expected_name):
    xml_author_data = PHDCBuilder()._build_author(family_name)
    author_string = ET.tostring(xml_author_data).decode()

    assert expected_oid in author_string
    assert expected_date in author_string
    assert expected_name in author_string


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
            (
                "<patient><name><prefix>Mr.</prefix><given>John</given>"
                + "<given>Jacob</given><family>Schmidt</family></name>"
                + '<administrativeGenderCode displayName="Male"/>'
                + '<sdtc:raceCode xmlns:sdtc="urn:hl7-org:sdtc" code="2106-3" '
                + 'codeSystem="2.16.840.1.113883.6.238" '
                + 'displayName="White" codeSystemName="Race &amp; Ethnicity"/>'
                + '<ethnicGroupCode code="2186-5" codeSystem="2.16.840.1.113883.6.238" '
                + 'displayName="Not Hispanic or Latino" '
                + 'codeSystemName="Race &amp; Ethnicity"/>'
                + "<birthTime>01-01-2000</birthTime>"
                + "</patient>"
            ),
        )
    ],
)
def test_build_patient(build_patient_test_data, expected_result):
    builder = PHDCBuilder()

    xml_patient_data = builder._build_patient(build_patient_test_data)
    assert ET.tostring(xml_patient_data).decode() == expected_result


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
                )
            ),
            (utils.read_file_from_assets("sample_phdc_header.xml")),
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
        b'xmlns="urn:hl7-org:v3" xmlns:sdtc="urn:hl7-org:sdtc" '
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


def test_get_case_report_code():
    builder = PHDCBuilder()
    case_report_code = builder._get_case_report_code()
    assert (
        ET.tostring(case_report_code)
        == b'<code code="55751-2" codeSystem="2.16.840.1.113883.6.1" '
        b'codeSystemName="LOINC" displayName="Public Health Case Report - PHRI"/>'
    )


@patch.object(uuid, "uuid4", lambda: "mocked-uuid")
def test_get_case_report():
    builder = PHDCBuilder()
    case_report_code = builder._build_case_report()

    assert (
        ET.tostring(case_report_code) == b"<component><section>"
        b'<id extension="mocked-uuid" assigningAuthorityName="LR"/>'
        b'<code code="55752-0"'
        b' codeSystem="2.16.840.1.113883.6.1" '
        b'codeSystemName="LOINC" '
        b'displayName="Clinical Information"/>'
        b"<title>Clinical Information</title>"
        b"</section></component>"
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
                    race_code="White",
                    ethnic_group_code="Not Hispanic or Latino",
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
            (utils.read_file_from_assets("sample_phdc.xml")),
        )
    ],
)
def test_build(build_header_test_data, expected_result):
    builder = PHDCBuilder()
    builder.set_input_data(build_header_test_data)
    phdc = builder.build()
    assert phdc.to_xml_string() == expected_result


def test_add_field():
    builder = PHDCBuilder()
    parent = ET.Element("parent")
    builder._add_field(parent, "test", "child")
    assert ET.tostring(parent) == b"<parent><child>test</child></parent>"
