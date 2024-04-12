import pathlib

from app.fhir.conversion.convert import add_rr_data_to_eicr
from lxml import etree


def test_add_rr_to_ecr():
    with open(pathlib.Path(__file__).parent / "assets" / "CDA_RR.xml") as fp:
        rr = fp.read()

    with open(pathlib.Path(__file__).parent / "assets" / "CDA_eICR.xml") as fp:
        ecr = fp.read()

    # extract rr fields, insert to ecr
    ecr = add_rr_data_to_eicr(rr, ecr)

    # confirm root tag added
    ecr_root = ecr.splitlines()[0]
    xsi_tag = "xmlns:xsi"
    assert xsi_tag in ecr_root

    # confirm new section added
    ecr = etree.fromstring(ecr)
    tag = "{urn:hl7-org:v3}" + "section"
    section = ecr.find(f"./{tag}", namespaces=ecr.nsmap)
    assert section is not None

    # confirm required elements added
    rr_tags = [
        "templateId",
        "id",
        "code",
        "title",
        "effectiveTime",
        "confidentialityCode",
        "entry",
    ]
    rr_tags = ["{urn:hl7-org:v3}" + tag for tag in rr_tags]
    for tag in rr_tags:
        element = section.find(f"./{tag}", namespaces=section.nsmap)
        assert element is not None

    # ensure that status has been pulled over
    entry_tag = "{urn:hl7-org:v3}" + "entry"
    template_id_tag = "{urn:hl7-org:v3}" + "templateId"
    code_tag = "{urn:hl7-org:v3}" + "code"
    for entry in section.find(f"./{entry_tag}", namespaces=section.nsmap):
        for temps in entry.findall(f"./{template_id_tag}", namespaces=entry.nsmap):
            status_code = entry.find(f"./{code_tag}", namespaces=entry.nsmap)
            assert temps is not None
            assert temps.attrib["root"] == "2.16.840.1.113883.10.20.15.2.3.29"
            assert "RRVS19" in status_code.attrib["code"]


def test_add_rr_to_ecr_rr_already_present(capfd):
    with open(pathlib.Path(__file__).parent / "assets" / "CDA_RR.xml") as fp:
        rr = fp.read()

    # This eICR has already been merged with an RR
    with open(pathlib.Path(__file__).parent / "assets" / "merged_eICR.xml") as fp:
        ecr = fp.read()

    merged_ecr = add_rr_data_to_eicr(rr, ecr)
    assert merged_ecr == ecr

    out, err = capfd.readouterr()
    assert "This eCR has already been merged with RR data." in out
