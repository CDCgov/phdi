from app.phdc.phdc import PHDCBuilder
from lxml import etree as ET


def test_build_telecom():
    # TODO: replace incoming_telecom_data with sample input once it has been
    #       constructed.

    # Test success
    incoming_telecom_data = {"phone": "+1-800-555-1234", "use": "WP"}
    expected_xml_telecom_data = '<telecom use="WP" value="+1-800-555-1234"/>'
    xml_telecom_data = PHDCBuilder._build_telecom(**incoming_telecom_data)
    assert ET.tostring(xml_telecom_data).decode() == expected_xml_telecom_data

    # Test when `use` is not included
    incoming_telecom_data = {"phone": "+1-800-555-1234"}
    expected_xml_telecom_data = '<telecom value="+1-800-555-1234"/>'
    xml_telecom_data = PHDCBuilder._build_telecom(**incoming_telecom_data)
    assert ET.tostring(xml_telecom_data).decode() == expected_xml_telecom_data

    # Test when `use` is None
    incoming_telecom_data = {"phone": "+1-800-555-1234", "use": None}
    expected_xml_telecom_data = '<telecom value="+1-800-555-1234"/>'
    xml_telecom_data = PHDCBuilder._build_telecom(**incoming_telecom_data)
    assert ET.tostring(xml_telecom_data).decode() == expected_xml_telecom_data
