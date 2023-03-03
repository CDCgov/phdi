import pathlib
from phdi.validation.validation import (
    _organize_messages,
    # _validate_attribute,
    # _validate_text,
    # _check_field_matches,
    # namespaces,
)


# Test file with known errors
sample_file_bad = open(
    pathlib.Path(__file__).parent.parent / "assets" / "ecr_sample_input_bad.xml"
).read()


# Test good file
sample_file_good = open(
    pathlib.Path(__file__).parent.parent / "assets" / "ecr_sample_input_good.xml"
).read()

config = open(
    pathlib.Path(__file__).parent.parent / "assets" / "sample_ecr_config.yaml"
).read()

# def test_validate_text():
#     actual_result = _validate_text("First Name", None)
#     print(actual_result)
#     assert 1 == 2

#     error_messages = []
#     for field in config.get("requiredFields"):
#         if not field.get("textRequired"):
#             continue
#         path = field.get("cdaPath")
#         matched_nodes_bad = sample_file_bad.xpath(path, namespaces=namespaces)
#         found_field = False

#         for node in matched_nodes_bad:
#             found, error_messages_from_node = _validate_text(field, node)
#             if found is True:
#                 found_field = True
#             if error_messages_from_node:
#                 error_messages += error_messages_from_node
#         if not found_field:
#             error_messages += ["Field not found: " + str(field)]

#     assert len(error_messages) == 3
#     assert (
#         error_messages[0] ==
#          "Field not found: {'fieldName': 'First Name', 'cdaPath': "
#         "'//hl7:ClinicalDocument/hl7:recordTarget/hl7:patientRole/"
#         "hl7:patient/hl7:name/hl7:given', 'textRequired': 'True', "
#         "'parent': 'name', 'parent_attributes': "
#         "[{'attributeName': 'use', 'regEx': 'L'}]}"
#     )
#     assert (
#         error_messages[1] == "Field not found: {'fieldName': 'City', 'cdaPath': "
#         "'//hl7:ClinicalDocument/hl7:recordTarget/hl7:patientRole/"
#         "hl7:addr/hl7:city', 'textRequired': 'True', "
#         "'parent': 'addr', 'parent_attributes': "
#         "[{'attributeName': 'use', 'regEx': 'H'}]}"
#     )

#     assert (
#         error_messages[2] == "Field: Zip does not match regEx: [0-9]{5}(?:-[0-9]{4})?"
#     )

#     error_messages = []
#     for field in config.get("requiredFields"):
#         if not field.get("textRequired"):
#             continue
#         path = field.get("cdaPath")
#         matched_nodes_good = sample_file_good.xpath(path, namespaces=namespaces)
#         found_field = False

#         for node in matched_nodes_good:
#             found, error_messages_from_node = _validate_text(field, node)
#             if found is True:
#                 found_field = True
#             if error_messages_from_node:
#                 error_messages += error_messages_from_node
#         if not found_field:
#             error_messages += ["Field not found: " + str(field)]
#     assert len(error_messages) == 0


# def test_validate_attribute_no_errors():
#     for field in config.get("requiredFields"):
#         if not field.get("attributes"):
#             continue
#         path = field.get("cdaPath")
#         matched_nodes = sample_file_good.xpath(path, namespaces=namespaces)
#         for node in matched_nodes:
#             results = _validate_attribute(field, node)
#             assert len(results) == 0


# def test_validate_attribute_with_errors():
#     for field in config.get("requiredFields"):
#         if not field.get("attributes"):
#             continue
#         path = field.get("cdaPath")
#         matched_nodes = sample_file_bad.xpath(path, namespaces=namespaces)
#         for node in matched_nodes:
#             results = _validate_attribute(field, node)
#             if (
#                 field.get("cdaPath") == "//hl7:ClinicalDocument/hl7:versionNumber"
#                 and field.get("attributes")[0].get("attributeName") == "value"
#             ):
#                 assert len(results) != 0


def test_organize_messages():
    errors = ["my error1", "my_error2"]
    warns = ["my warn1"]
    infos = ["", "SOME"]

    expected_result = {"errors": errors, "warnings": warns, "information": infos}

    actual_result = _organize_messages(errors, warns, infos)
    assert actual_result == expected_result
