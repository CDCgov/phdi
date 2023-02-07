from lxml import etree
from pathlib import Path

ecr_p = Path(__file__).with_name("ecr_sample_input.xml")
fp = open(ecr_p, "r")
tree = etree.parse(fp)
# tree = etree.XML(bytes(page, encoding="utf-8"))
# print(etree.tostring(tree, pretty_print=True))

namespaces = {
    "hl7": "urn:hl7-org:v3",
    "xsi": "http://www.w3.org/2005/Atom",
    "cda": "urn:hl7-org:v3",
    "sdtc": "urn:hl7-org:sdtc",
    "voc": "http://www.lantanagroup.com/voc",
}


r = tree.xpath("//hl7:ClinicalDocument/hl7:id", namespaces=namespaces)
print(r[0].get("root"))
# for node in r:
#     print(node[0])

# from elementtree import ElementTree as ET
# ecr_p = Path(__file__).with_name("ecr_sample_input.xml")
# fp = open(ecr_p, "r")
# element = etree.parse(fp)
# e = element.findall("ClinicalDocument/recordTarget/patientRole/patient/name/given")
# print(e)
