from lxml import etree
from pathlib import Path
import re

config = {
    "requiredFields": [
        # {
        #     "fieldName": "Status",
        #     "cdaPath": "//hl7:ClinicalDocument/hl7:component/hl7:structuredBody/hl7:component/hl7:section/hl7:entry/hl7:act/hl7:code",
        #     "attributes": [{"attributeName": "code"}],
        # },
        # {
        #     "fieldName": "Conditions",
        #     "cdaPath": "//hl7:ClinicalDocument/hl7:component/hl7:structuredBody/hl7:component/hl7:section/hl7:entry/hl7:organizer/hl7:component/hl7:observation/hl7:value/hl7:code",
        #     "textRequired": True,
        # },
        {
            "fieldName": "eICR",
            "cdaPath": "//hl7:ClinicalDocument/hl7:id",
            "attributes": [{"attributeName": "root"}],
        },
        # {
        #     "fieldName": "eICR Version Number",
        #     "cdaPath": "//hl7:ClinicalDocument/hl7:versionNumber",
        #     "attributes": [{"attributeName": "value"}],
        # },
        # {
        #     "fieldName": "Authoring date/hl7:time",
        #     "cdaPath": "//hl7:ClinicalDocument/hl7:recordTarget/hl7:author/hl7:time",
        #     "attributes": [{"attributeName": "value"}],
        # },
        {
            "fieldName": "First Name",
            "cdaPath": "//hl7:ClinicalDocument/hl7:recordTarget/hl7:patientRole/hl7:patient/hl7:name",
            "textRequired": True,
            "attributes": [{"attributeName": "use", "regEx": "/L/"}],
        },
        # {
        #     "fieldName": "Middle Name",
        #     "cdaPath": "//hl7:ClinicalDocument/hl7:recordTarget/hl7:patientRole/hl7:patient/hl7:name/hl7:given",
        #     "textRequired": True,
        #     "attributes": [
        #         {"attributeName": "use", "regEx": "/L/"},
        #         {"attributeName": "qualifer", "regEx": "/IN/"},
        #     ],
        # },
        # {
        #     "fieldName": "Last Name",
        #     "cdaPath": "//hl7:ClinicalDocument/hl7:recordTarget/hl7:patientRole/hl7:patient/hl7:name/hl7:family",
        #     "attributes": [{"attributeName": "use", "regEx": "/L/"}],
        #     "textRequired": True,
        # },
        # {
        #     "fieldName": "DOB",
        #     "cdaPath": "//hl7:ClinicalDocument/hl7:recordTarget/hl7:patientRole/hl7:patient/hl7:birthTime",
        #     "textRequired": True,
        # },
        # {
        #     "fieldName": "MRN",
        #     "cdaPath": "//hl7:ClinicalDocument/hl7:recordTarget/hl7:patientRole/hl7:id/hl7:",
        #     "attributes": [{"attributeName": "extension"}, {"attributeName": "root"}],
        # },
        # {
        #     "fieldName": "Sex",
        #     "cdaPath": "//hl7:ClinicalDocument/hl7:recordTarget/hl7:patientRole/hl7:patient/hl7:administrativeGenderCode",
        #     "textRequired": True,
        #     "regEx": "/F|M|O|U/",
        # },
        # {
        #     "fieldName": "Street Address",
        #     "cdaPath": "//hl7:ClinicalDocument/hl7:recordTarget/hl7:patientRole/hl7:addr/hl7:streetAddressLine",
        #     "textRequired": True,
        # },
        # {
        #     "fieldName": "City",
        #     "cdaPath": "//hl7:ClinicalDocument/hl7:recordTarget/hl7:patientRole/hl7:addr/hl7:city",
        #     "textRequired": True,
        # },
        # {
        #     "fieldName": "State",
        #     "cdaPath": "//hl7:ClinicalDocument/hl7:recordTarget/hl7:patientRole/hl7:addr/hl7:state",
        #     "textRequired": True,
        # },
        # {
        #     "fieldName": "Country",
        #     "cdaPath": "//hl7:ClinicalDocument/hl7:recordTarget/hl7:patientRole/hl7:addr/hl7:country",
        #     "textRequired": True,
        # },
        # {
        #     "fieldName": "Zip",
        #     "cdaPath": "//hl7:ClinicalDocument/hl7:recordTarget/hl7:patientRole/hl7:addr/hl7:postalCode",
        #     "textRequired": True,
        #     "regEx": "/[0-9]{5}(?:-[0-9]{4})?/",
        # },
        # {
        #     "fieldName": "Provider ID",
        #     "cdaPath": "//hl7:ClinicalDocument/hl7:componentOf/hl7:encompassingEncounter/hl7:responsibleParty/hl7:assignedEntity/hl7:id",
        #     "attributes": [{"attributeName": "extension"}, {"attributeName": "root"}],
        # },
    ]
}

namespaces = {
    "hl7": "urn:hl7-org:v3",
    "xsi": "http://www.w3.org/2005/Atom",
    "cda": "urn:hl7-org:v3",
    "sdtc": "urn:hl7-org:sdtc",
    "voc": "http://www.lantanagroup.com/voc",
}


def get_parsed_file(file_name):
    ecr_path = Path(__file__).with_name(file_name)
    file = open(ecr_path, "r")
    return etree.parse(file)


def validate(file_name, config):
    tree = get_parsed_file(file_name)
    for field in config.get("requiredFields"):
        path = field.get("cdaPath")
        matched_node = tree.xpath(path, namespaces=namespaces)
        # attributes check
        validate_attribute(field, matched_node)
        # text check
        validate_text


def validate_attribute(field, matched_node):
    attribute_value = ""
    for attribute in field.get("attributes"):
        if "attributeName" in attribute:
            attribute_name = attribute.get("attributeName")
            attribute_value = matched_node[0].get(attribute_name)
            print(attribute_value)
        if "regEx" in attribute:
            pattern = re.compile(attribute.get("regEx"))
            print(pattern)
            print(pattern.match(attribute_value))


def validate_text():
    pass


def main():
    validate("ecr_sample_input.xml", config)


main()
