from datetime import datetime

import pytest
from app.phdc.phdc import PHDCBuilder
from lxml import etree as ET


@pytest.mark.parametrize(
    "build_telecom_test_data, expected_result",
    [
        # Success with `use`
        (
            {"phone": "+1-800-555-1234", "use": "WP"},
            '<telecom use="WP" value="+1-800-555-1234"/>',
        ),
        # Success without `use`
        (
            {
                "phone": "+1-800-555-1234",
            },
            '<telecom value="+1-800-555-1234"/>',
        ),
        # Success with `use` as None
        (
            {"phone": "+1-800-555-1234", "use": None},
            '<telecom value="+1-800-555-1234"/>',
        ),
    ],
)
def test_build_telecom(build_telecom_test_data, expected_result):
    builder = PHDCBuilder()
    xml_telecom_data = builder._build_telecom(**build_telecom_test_data)
    assert ET.tostring(xml_telecom_data).decode() == expected_result


@pytest.mark.parametrize(
    "build_addr_test_data, expected_result",
    [
        # Success with all values present
        (
            {
                "use": "H",
                "line": "123 Main Street",
                "city": "Brooklyn",
                "state": "New York",
                "zip": "11205",
                "county": "Kings",
                "country": "USA",
            },
            (
                '<addr use="H"><streetAddressLine>123 Main Street</streetAddressLine>'
                + "<city>Brooklyn</city><state>New York</state>"
                + "<postalCode>11205</postalCode><county>Kings</county>"
                + "<country>USA</country></addr>"
            ),
        ),
        # Success with some values missing
        (
            {
                "use": "H",
                "line": "123 Main Street",
                "city": "Brooklyn",
                "state": "New York",
            },
            (
                '<addr use="H"><streetAddressLine>123 Main Street</streetAddressLine>'
                + "<city>Brooklyn</city><state>New York</state></addr>"
            ),
        ),
        # Success with some values as None
        (
            {
                "use": "H",
                "line": "123 Main Street",
                "city": "Brooklyn",
                "state": None,
            },
            (
                '<addr use="H"><streetAddressLine>123 Main Street</streetAddressLine>'
                + "<city>Brooklyn</city></addr>"
            ),
        ),
    ],
)
def test_build_addr(build_addr_test_data, expected_result):
    builder = PHDCBuilder()
    xml_addr_data = builder._build_addr(**build_addr_test_data)
    assert ET.tostring(xml_addr_data).decode() == expected_result


@pytest.mark.parametrize(
    "build_name_test_data, expected_result",
    [
        # Success with all single given_name
        (
            {
                "use": "L",
                "prefix": "Mr.",
                "given_name": "John",
                "last_name": "Doe",
            },
            (
                '<name use="L"><prefix>Mr.</prefix>'
                + "<given>John</given><family>Doe</family></name>"
            ),
        ),
        # Success with given_name as list
        (
            {
                "use": "L",
                "prefix": "Mr.",
                "given_name": ["John", "Jacob"],
                "last_name": "Doe",
            },
            (
                '<name use="L"><prefix>Mr.</prefix>'
                + "<given>John</given><given>Jacob</given><family>Doe</family></name>"
            ),
        ),
        # Success with given_name as multi-name str
        (
            {
                "use": "L",
                "prefix": "Mr.",
                "given_name": "John Jacob",
                "last_name": "Doe",
            },
            (
                '<name use="L"><prefix>Mr.</prefix>'
                + "<given>John</given><given>Jacob</given><family>Doe</family></name>"
            ),
        ),
        # Success with more than 2 given names in a string condensed to 2 given names
        (
            {
                "use": "L",
                "prefix": "Mr.",
                "given_name": "John Jacob Jingleheimer",
                "last_name": "Doe",
            },
            (
                '<name use="L"><prefix>Mr.</prefix>'
                + "<given>John</given><given>Jacob Jingleheimer</given>"
                + "<family>Doe</family></name>"
            ),
        ),
        # Success with more than 2 given names in a list condensed to 2 given names
        (
            {
                "use": "L",
                "prefix": "Mr.",
                "given_name": ["John", "Jacob", "Jingleheimer"],
                "last_name": "Doe",
            },
            (
                '<name use="L"><prefix>Mr.</prefix>'
                + "<given>John</given><given>Jacob Jingleheimer</given>"
                + "<family>Doe</family></name>"
            ),
        ),
    ],
)
def test_build_name(build_name_test_data, expected_result):
    builder = PHDCBuilder()
    xml_name_data = builder._build_name(**build_name_test_data)
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


@pytest.mark.parametrize(
    "family_name, expected_oid, expected_date, expected_name",
    [
        # test for correct OID and name "CDC PRIME DIBBs"
        (
            "CDC PRIME DIBBs",
            "2.16.840.1.113883.19.5",
            datetime.now().strftime("%Y%m%d"),
            (
                '<author><time value="{}"/><assignedAuthor>'
                '<id root="2.16.840.1.113883.19.5"/><name>'
                "<family>CDC PRIME DIBBs</family></name>"
                "</assignedAuthor></author>"
            ).format(datetime.now().strftime("%Y%m%d%H%M%S")),
        ),
        # test for correct OID and name "Local Health Jurisdiction"
        (
            "Local Health Jurisdiction",
            "2.16.840.1.113883.19.5",
            datetime.now().strftime("%Y%m%d"),
            (
                '<author><time value="{}"/><assignedAuthor>'
                '<id root="2.16.840.1.113883.19.5"/><name>'
                "<family>Local Health Jurisdiction</family></name>"
                "</assignedAuthor></author>"
            ).format(datetime.now().strftime("%Y%m%d%H%M%S")),
        ),
    ],
)
def test_build_author(family_name, expected_oid, expected_date, expected_name):
    xml_author_data = PHDCBuilder()._build_author(family_name)
    author_string = ET.tostring(xml_author_data).decode()

    assert expected_oid in author_string
    assert expected_date in author_string
    assert expected_name in author_string


def create_patient_test_data():
    builder = PHDCBuilder()
    n_data = {
        "prefix": "Mr.",
        "given_name": "John Jacob",
        "last_name": "Schmidt",
    }
    name_data = builder._build_name(**n_data)
    t_data = {"phone": "+1-800-555-1234", "use": "WP"}
    telecom_data = builder._build_telecom(**t_data)

    return {
        "complete_data": {
            "name_data": name_data,
            "telecom_data": telecom_data,
            "administrativeGenderCode": "Male",
            "raceCode": "White",
            "ethnicGroupCode": "Not-Hispanic/Latino",
            "birthTime": "01-01-2000",
        },
        "missing_data": {
            "name_data": name_data,
            "telecom_data": telecom_data,
            "administrativeGenderCode": "Male",
            "raceCode": "White",
            "ethnicGroupCode": None,
            "birthTime": "01-01-2000",
        },
    }


patient_test_data = create_patient_test_data()


@pytest.mark.parametrize(
    "build_patient_test_data, expected_result",
    [
        # Success with all patient data
        (
            patient_test_data["complete_data"],
            (
                "<patient><name><prefix>Mr.</prefix><given>John</given>"
                + "<given>Jacob</given><family>Schmidt</family></name>"
                + '<telecom use="WP" value="+1-800-555-1234"/>'
                + '<administrativeGenderCode displayName="Male"/>'
                + '<raceCode displayName="White"/><ethnicGroupCode displayName='
                + '"Not-Hispanic/Latino"/><birthTime>01-01-2000</birthTime></patient>'
            ),
        ),
        # Success with one patient data element as None
        (
            patient_test_data["missing_data"],
            (
                "<patient><name><prefix>Mr.</prefix><given>John</given><given>Jacob"
                + '</given><family>Schmidt</family></name><telecom use="WP"'
                + ' value="+1-800-555-1234"/><administrativeGenderCode displayName='
                + '"Male"/><raceCode displayName="White"/><birthTime>01-01-2000'
                + "</birthTime></patient>"
            ),
        ),
    ],
)
def test_build_patient(build_patient_test_data, expected_result):
    builder = PHDCBuilder()

    xml_patient_data = builder._build_patient(**build_patient_test_data)
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
            xml_recordtarget_data = builder._build_recordTarget(**build_rt_test_data)
            assert str(e.value) == str(expected_result)

    else:
        xml_recordtarget_data = builder._build_recordTarget(**build_rt_test_data)
        assert ET.tostring(xml_recordtarget_data).decode() == expected_result

def test_build_header():
    print()
    print(
        ET.tostring(
            PHDCBuilder._build_header(),
            pretty_print=True,
            xml_declaration=True,
            encoding="utf-8",
        ).decode()
    )
