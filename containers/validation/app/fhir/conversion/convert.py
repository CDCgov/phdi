from lxml import etree


def add_rr_data_to_eicr(rr, ecr):
    """
    Extracts relevant fields from an RR document, and inserts them into a
    given eICR document. Ensures that the eICR contains properly formatted
    RR fields, including templateId, id, code, title, effectiveTime,
    confidentialityCode, and corresponding entries; and required format tags.

    :param rr: A serialized xml format reportability response (RR) document.
    :param ecr: A serialized xml format electronic initial case report (eICR) document.
    :return: An xml format eICR document with additional fields extracted from the RR.
    """
    # add xmlns:xsi attribute if not there
    lines = ecr.splitlines()
    xsi_tag = "xmlns:xsi"
    if xsi_tag not in lines[0]:
        lines[0] = lines[0].replace(
            'xmlns="urn:hl7-org:v3"',
            'xmlns="urn:hl7-org:v3" '
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
        )
        ecr = "\n".join(lines)

    rr = etree.fromstring(rr)
    ecr = etree.fromstring(ecr)

    if ecr.xpath('//*[@code="88085-6"]'):
        print("This eCR has already been merged with RR data.")
        return etree.tostring(ecr, encoding="unicode", method="xml")

    # Create the tags for elements we'll be looking for
    rr_tags = [
        "templateId",
        "id",
        "code",
        "title",
        "effectiveTime",
        "confidentialityCode",
    ]
    rr_tags = ["{urn:hl7-org:v3}" + tag for tag in rr_tags]
    rr_elements = []

    # Find root-level elements and add them to a list
    for tag in rr_tags:
        rr_elements.append(rr.find(f"./{tag}", namespaces=rr.nsmap))

    # Find the nested entry element that we need
    entry_tag = "{urn:hl7-org:v3}" + "component/structuredBody/component/section/entry"
    rr_nested_entries = rr.findall(f"./{entry_tag}", namespaces=rr.nsmap)

    organizer_tag = "{urn:hl7-org:v3}" + "organizer"

    # For now we assume there is only one matching entry
    rr_entry = None
    for entry in rr_nested_entries:
        if entry.attrib and "DRIV" in entry.attrib["typeCode"]:
            organizer = entry.find(f"./{organizer_tag}", namespaces=entry.nsmap)
            if (
                organizer is not None
                and "CLUSTER" in organizer.attrib["classCode"]
                and "EVN" in organizer.attrib["moodCode"]
            ):
                rr_entry = entry
                exit

    # find the status in the RR utilizing the templateid root
    # codes specified from the APHL/LAC Spec
    base_tag_for_status = (
        "{urn:hl7-org:v3}" + "component/structuredBody/component/section"
    )
    template_id_tag = "{urn:hl7-org:v3}" + "templateId"
    entry_status_tag = "{urn:hl7-org:v3}" + "entry"
    act_status_tag = "{urn:hl7-org:v3}" + "act"
    sections_for_status = rr.findall(f"./{base_tag_for_status}", namespaces=rr.nsmap)
    rr_entry_for_status_codes = None
    for status_section in sections_for_status:
        template_id = status_section.find(
            f"./{template_id_tag}", namespaces=status_section.nsmap
        )
        if (
            template_id is not None
            and "2.16.840.1.113883.10.20.15.2.2.3" in template_id.attrib["root"]
        ):
            for entry in status_section.findall(
                f"./{entry_status_tag}", namespaces=status_section.nsmap
            ):
                for act in entry.findall(f"./{act_status_tag}", namespaces=entry.nsmap):
                    entry_act_template_id = act.find(
                        f"./{template_id_tag}", namespaces=act.nsmap
                    )
                    if (
                        entry_act_template_id is not None
                        and "2.16.840.1.113883.10.20.15.2.3.29"
                        in entry_act_template_id.attrib["root"]
                    ):
                        # only anticipating one status code
                        rr_entry_for_status_codes = entry
                        exit

    # Create the section element with root-level elements
    # and entry to insert in the eICR
    ecr_section = None
    if rr_entry is not None:
        ecr_section_tag = "{urn:hl7-org:v3}" + "section"
        ecr_section = etree.Element(ecr_section_tag)
        ecr_section.extend(rr_elements)
        if rr_entry_for_status_codes is not None:
            ecr_section.append(rr_entry_for_status_codes)
        ecr_section.append(rr_entry)

        # Append the ecr section into the eCR - puts it at the end
        ecr.append(ecr_section)

    ecr = etree.tostring(ecr, encoding="unicode", method="xml")

    return ecr
