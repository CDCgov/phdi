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
