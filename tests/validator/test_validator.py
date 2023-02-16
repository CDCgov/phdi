import yaml
from phdi.validator.validate import validate_text, get_parsed_file
from pathlib import Path

namespaces = {
    "hl7": "urn:hl7-org:v3",
    "xsi": "http://www.w3.org/2005/Atom",
    "cda": "urn:hl7-org:v3",
    "sdtc": "urn:hl7-org:sdtc",
    "voc": "http://www.lantanagroup.com/voc",
}


def test_validate_text():
    with open("schema.yml") as f:
        # use safe_load instead load
        schema = yaml.safe_load(f)

        # Test file with known errors
        sample_file_bad = get_parsed_file(
            Path(__file__).parent / "ecr_sample_input_bad.xml"
        )
        error_messages = []
        for field in schema.get("requiredFields"):
            if not field.get("textRequired"):
                continue
            path = field.get("cdaPath")
            matched_nodes_bad = sample_file_bad.xpath(path, namespaces=namespaces)
            matched_nodes_good = sample_file_bad.xpath(path, namespaces=namespaces)
            found_field = False

            for node in matched_nodes_bad:
                found, error_messages_from_node = validate_text(field, node)
                if found is True:
                    found_field = True
                if error_messages_from_node:
                    error_messages += error_messages_from_node
            if not found_field:
                error_messages += ["Field not found: " + str(field)]
            assert len(error_messages) == 1
            assert (
                error_messages[0]
                == "Field not found: {'fieldName': 'First Name', 'nodeName': 'given', 'cdaPath': '//hl7:ClinicalDocument/hl7:recordTarget/hl7:patientRole/hl7:patient/hl7:name/hl7:given', 'textRequired': 'True', 'parent': 'name', 'parent_attributes': [{'attributeName': 'use', 'regEx': 'L'}]}"
            )

        # Test good file
        sample_file_good = get_parsed_file(
            Path(__file__).parent / "ecr_sample_input_good.xml"
        )
        error_messages = []
        for field in schema.get("requiredFields"):
            if not field.get("textRequired"):
                continue
            path = field.get("cdaPath")
            matched_nodes_good = sample_file_good.xpath(path, namespaces=namespaces)
            found_field = False

            for node in matched_nodes_good:
                found, error_messages_from_node = validate_text(field, node)
                if found is True:
                    found_field = True
                if error_messages_from_node:
                    error_messages += error_messages_from_node
            if not found_field:
                error_messages += ["Field not found: " + str(field)]
            assert len(error_messages) == 0
