import yaml

from phdi.validation.validate import validate_text, get_parsed_file, validate_attribute
from pathlib import Path

namespaces = {
    "hl7": "urn:hl7-org:v3",
    "xsi": "http://www.w3.org/2005/Atom",
    "cda": "urn:hl7-org:v3",
    "sdtc": "urn:hl7-org:sdtc",
    "voc": "http://www.lantanagroup.com/voc",
}

# Test file with known errors
sample_file_bad = get_parsed_file(
    Path(__file__).parent / "../assets/ecr_sample_input_bad.xml"
)

# Test good file
sample_file_good = get_parsed_file(
    Path(__file__).parent / "../assets/ecr_sample_input_good.xml"
)

schema_path = "../assets/schema.yml"


def test_validate_text():
    with open(schema_path) as f:
        # use safe_load instead load
        schema = yaml.safe_load(f)

        error_messages = []
        for field in schema.get("requiredFields"):
            if not field.get("textRequired"):
                continue
            path = field.get("cdaPath")
            matched_nodes_bad = sample_file_bad.xpath(path, namespaces=namespaces)
            found_field = False

            for node in matched_nodes_bad:
                found, error_messages_from_node = validate_text(field, node)
                if found is True:
                    found_field = True
                if error_messages_from_node:
                    error_messages += error_messages_from_node
            if not found_field:
                error_messages += ["Field not found: " + str(field)]

        assert len(error_messages) == 3
        assert (
            error_messages[0]
            == "Field not found: {'fieldName': 'First Name', 'cdaPath': '//hl7:ClinicalDocument/hl7:recordTarget/hl7:patientRole/hl7:patient/hl7:name/hl7:given', 'textRequired': 'True', 'parent': 'name', 'parent_attributes': [{'attributeName': 'use', 'regEx': 'L'}]}"
        )
        assert (
            error_messages[1]
            == "Field not found: {'fieldName': 'City', 'cdaPath': '//hl7:ClinicalDocument/hl7:recordTarget/hl7:patientRole/hl7:addr/hl7:city', 'textRequired': 'True', 'parent': 'addr', 'parent_attributes': [{'attributeName': 'use', 'regEx': 'H'}]}"
        )

        assert (
            error_messages[2]
            == "Field: Zip does not match regEx: [0-9]{5}(?:-[0-9]{4})?"
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


def test_validate_attribute_no_errors():
    with open(schema_path) as f:
        schema = yaml.safe_load(f)
        for field in schema.get("requiredFields"):
            if not field.get("attributes"):
                continue
            path = field.get("cdaPath")
            matched_nodes = sample_file_good.xpath(path, namespaces=namespaces)
            for node in matched_nodes:
                results = validate_attribute(field, node)
                assert len(results) == 0


def test_validate_attribute_with_errors():
    with open(schema_path) as f:
        schema = yaml.safe_load(f)
        for field in schema.get("requiredFields"):

            if not field.get("attributes"):
                continue
            path = field.get("cdaPath")
            matched_nodes = sample_file_good.xpath(path, namespaces=namespaces)
            for node in matched_nodes:
                results = validate_attribute(field, node)
                if (
                    field.get("cdaPath") == "//hl7:ClinicalDocument/hl7:versionNumber"
                    and field.get("attributes")[0].get("attributeName") == "value"
                ):
                    print(results)
                    assert len(results) != 0
