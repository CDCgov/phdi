import pytest
from app.phdc.phdc import PHDC
from app.phdc.phdc import PHDCBuilder
from app.phdc.phdc import PHDCDirector
from lxml import etree as ET


@pytest.fixture
def builder():
    return PHDCBuilder()


@pytest.fixture
def director(builder):
    return PHDCDirector(builder)


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
def test_build_telecom(builder, build_telecom_test_data, expected_result):
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
def test_build_addr(builder, build_addr_test_data, expected_result):
    xml_addr_data = builder._build_addr(**build_addr_test_data)
    assert ET.tostring(xml_addr_data).decode() == expected_result


@pytest.fixture
def director_data():
    return {
        "telecom_data": {"phone": "+1-800-555-1234", "use": "WP"},
        "addr_data": {
            "use": "H",
            "line": "123 Main Street",
            "city": "Brooklyn",
            "state": "New York",
            "zip": "11205",
            "county": "Kings",
            "country": "USA",
        },
    }


def test_director_build_case_report(director, director_data):
    case_report = director.build_case_report(**director_data)
    assert isinstance(case_report, PHDC)
