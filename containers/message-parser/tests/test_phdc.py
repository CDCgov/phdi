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
    xml_telecom_data = PHDCBuilder._build_telecom(**build_telecom_test_data)
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
    xml_addr_data = PHDCBuilder._build_addr(**build_addr_test_data)
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
    xml_name_data = PHDCBuilder._build_name(**build_name_test_data)
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
    if isinstance(expected_result, ValueError):
        with pytest.raises(ValueError) as e:
            xml_custodian_data = PHDCBuilder._build_custodian(
                **build_custodian_test_data
            )
            assert str(e.value) == str(expected_result)

    else:
        xml_custodian_data = PHDCBuilder._build_custodian(**build_custodian_test_data)
        assert ET.tostring(xml_custodian_data).decode() == expected_result
