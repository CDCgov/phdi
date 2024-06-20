from lxml import etree as ET

from app.utils import load_section_loincs
from app.utils import read_json_from_assets

# LOINC codes for eICR sections our refiner API accepts
SECTION_LOINCS, SECTION_DETAILS = load_section_loincs(
    read_json_from_assets("section_loincs.json")
)


def validate_message(raw_message: str) -> tuple[bytes | None, str]:
    """
    Validates that an incoming XML message can be parsed by lxml's etree .

    :param raw_message: The XML input.
    :return: The validation result as a string.
    """
    error_message = ""
    try:
        validated_message = ET.fromstring(raw_message)
        return (validated_message, error_message)
    except ET.XMLSyntaxError as e:
        error_message = f"XMLSyntaxError: {e}"
        return (None, str(error_message))


def validate_sections_to_include(sections_to_include: str | None) -> tuple[list, str]:
    """
    Validates the sections to include in the refined message and returns them as a list
    of corresponding LOINC codes.

    :param sections_to_include: The sections to include in the refined message.
    :raises ValueError: When at least one of the sections_to_inlcude is invalid.
    :return: A tuple that includes the sections to include in the refined message as a
    list of LOINC codes corresponding to the sections and an error message. If there is
    no error in validating the sections to include, the error message will be an empty
    string.
    """
    if sections_to_include in [None, ""]:
        return (None, "")

    section_loincs = []
    sections = sections_to_include.split(",")
    for section in sections:
        if section not in SECTION_LOINCS:
            error_message = f"{section} is invalid. Please provide a valid section."
            return (section_loincs, error_message)
        section_loincs.append(section)

    return (section_loincs, "")


def refine(
    validated_message: bytes,
    sections_to_include: list = None,
    clinical_services: list = None,
) -> str:
    """
    Refines an incoming XML message based on the sections to include and/or
    the clinical services found based on inputted section LOINC codes or
    condition SNOMED codes. This will then loop through the dynamic XPaths to
    create an XPath to refine the XML.

    :param validated_message: The XML input.
    :param sections_to_include: The sections to include in the refined message.
    :param clinical_services: clinical service XPaths to include in the
    refined message.
    :return: The refined message.
    """
    header = _select_message_header(validated_message)
    namespaces = {"hl7": "urn:hl7-org:v3"}
    elements = []

    # TODO: capture sections with trigger code templates before refining

    # if no parameters are provided, return the header with all sections
    # and do not include trigger_code_sections
    if not sections_to_include and not clinical_services:
        xpath_expression = "//*[local-name()='section']"
        elements = validated_message.xpath(xpath_expression, namespaces=namespaces)
        return _add_root_element(header, elements)

    # start with sections_to_include param
    if sections_to_include:
        sections_xpaths = " or ".join(
            [f"@code='{section}'" for section in sections_to_include]
        )
        sections_xpath_expression = (
            f"//*[local-name()='section'][hl7:code[{sections_xpaths}]]"
        )

    # we need to find the condition codes in the clinical_services list and then
    # extract the section LOINC codes
    if clinical_services:
        # join the xpath expressions together
        services_xpath_expression = " | ".join(clinical_services)
        # grab all of the <entry> elements with the clinical_service codes
        service_elements = validated_message.xpath(
            services_xpath_expression, namespaces=namespaces
        )
        # initialize a dictionary to hold the section code and the element
        services_section_and_elements = {}
        for element in service_elements:
            # the parent is the section element
            parent = element.getparent()
            # find the code element and extract the section LOINC
            code_element = parent.find(".//hl7:code", namespaces=namespaces)
            code = code_element.get("code")
            # as we create the dictionary, we want to make sure the section key is unique
            if code not in services_section_and_elements:
                services_section_and_elements[code] = []
            # append (<entry>) element to corresponding section key
            services_section_and_elements[code].append(element)

    # if we only have sections_to_include then we need to create minimal sections
    # for the sections not included and if trigger_code_sections overlap with sections_to_include
    # then we do not need to include trigger_code_sections; however, if trigger_code_sections fall
    # outside of sections_to_include then we need to append them to the minimal sections
    if sections_to_include and not clinical_services:
        minimal_sections = _create_minimal_sections(sections_to_include)
        xpath_expression = sections_xpath_expression
        elements = validated_message.xpath(xpath_expression, namespaces=namespaces)
        return _add_root_element(header, elements + minimal_sections)

    # if we only have clinical_services then we use the unique sections from the
    # services_section_and_elements dictionary to include entries to sections + minimal sections
    # if no sections_to_include are provided and check for overlap with trigger_code_sections
    # and either remove trigger_code_sections if it already exists, or append to the
    # correct section of minimal sections or refined section
    if clinical_services and not sections_to_include:
        elements = []
        for section_code, entries in services_section_and_elements.items():
            minimal_section = _create_minimal_section(section_code, empty_section=False)
            for entry in entries:
                minimal_section.append(entry)
            elements.append(minimal_section)
        minimal_sections = _create_minimal_sections(
            sections_with_conditions=services_section_and_elements.keys(),
            empty_section=True,
        )
        return _add_root_element(header, elements + minimal_sections)

    # if we have both sections_to_include and clinical_services then we need to
    # prioritize the clinical_services using the sections_to_include as a locus; if
    # there is overlap with trigger_code_sections, then we do not need to include them.
    # if there is no overlap, we need to append to either the refined section or the
    # minimal sections
    if sections_to_include and clinical_services:
        # check if there is match between sections_to_include and conditions  we want to include
        # if there is a match, these are the _only_ sections we want to include
        matching_sections = set(sections_to_include) & set(
            services_section_and_elements.keys()
        )
        # if there is no match, we will respond with empty; minimal sections
        if not matching_sections:
            minimal_sections = _create_minimal_sections()
            return _add_root_element(header, minimal_sections)

        elements = []
        for section_code in matching_sections:
            minimal_section = _create_minimal_section(section_code, empty_section=False)
            for entry in services_section_and_elements[section_code]:
                minimal_section.append(entry)
            elements.append(minimal_section)

        minimal_sections = _create_minimal_sections(
            sections_with_conditions=matching_sections,
            empty_section=True,
        )

        return _add_root_element(header, elements + minimal_sections)


def _create_minimal_section(section_code: str, empty_section: bool) -> ET.Element:
    """
    Helper function to create a minimal section element based on the LOINC section code.

    :param section_code: The LOINC code of the section to create a minimal section for.
    :param empty_section: Whether the section should be empty and include a nullFlavor attribute.
    :return: A minimal section element or None if the section code is not recognized.
    """
    if section_code not in SECTION_DETAILS:
        return None

    # display_name, template_root, template_extension, title_text = SECTION_DETAILS[
    #     section_code
    # ]

    minimal_fields = SECTION_DETAILS[section_code]["minimal_fields"]
    display_name = minimal_fields["display_name"]
    template_root = minimal_fields["template_id_root"]
    template_extension = minimal_fields["template_id_extension"]
    title_text = minimal_fields["title"]

    section = ET.Element("section")
    if empty_section:
        section.set("nullFlavor", "NI")

    templateId1 = ET.Element(
        "templateId", root=template_root, extension=template_extension
    )
    section.append(templateId1)

    code = ET.Element(
        "code",
        code=section_code,
        codeSystem="2.16.840.1.113883.6.1",
        displayName=display_name,
    )
    section.append(code)

    title = ET.Element("title")
    title.text = title_text
    section.append(title)

    text_elem = ET.Element("text")
    if empty_section:
        text_elem.text = "Removed via PRIME DIBBs Message Refiner API endpoint by Public Health Authority"
    else:
        text_elem.text = "Only entries that match the corresponding condition code were included in this section via PRIME DIBBs Message Refiner API endpoint by Public Health Authority"
    section.append(text_elem)

    return section


def _create_minimal_sections(
    sections_to_include: list = None,
    sections_with_conditions: list = None,
    empty_section: bool = True,
) -> list:
    """
    Creates minimal sections for sections not included in sections_to_include.

    :param sections_to_include: The sections to include in the refined message.
    :param sections_with_conditions: Sections that have condition-specific entries.
    :param empty_section: Whether the sections should be empty and include a nullFlavor attribute.
    :return: List of minimal section elements.
    """
    minimal_sections = []
    sections_to_exclude = (
        set(SECTION_DETAILS.keys())
        - set(sections_to_include or [])
        - set(sections_with_conditions or [])
    )

    for section_code in sections_to_exclude:
        minimal_section = _create_minimal_section(section_code, empty_section)
        if minimal_section is not None:
            minimal_sections.append(minimal_section)
    return minimal_sections


def _add_root_element(header: bytes, elements: list) -> str:
    """
    This helper function sets up and creates a new root element for the XML
    by using a combination of a direct namespace uri and nsmap to ensure that
    the default namespaces are set correctly.
    :param header: The header section of the XML.
    :param elements: List of refined elements found in XML.
    :return: The full refined XML, formatted as a string.
    """
    namespace = "urn:hl7-org:v3"
    nsmap = {
        None: namespace,
        "cda": namespace,
        "sdtc": "urn:hl7-org:sdtc",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    }
    # creating the root element with our uri namespace and nsmap
    refined_message_root = ET.Element(f"{{{namespace}}}ClinicalDocument", nsmap=nsmap)
    for h in header:
        refined_message_root.append(h)
    # creating the component element and structuredBody element with the same namespace
    # and adding them to the new root
    main_component = ET.SubElement(refined_message_root, f"{{{namespace}}}component")
    structuredBody = ET.SubElement(main_component, f"{{{namespace}}}structuredBody")

    # Append the filtered elements to the new root and use the uri namespace
    for element in elements:
        section_component = ET.SubElement(structuredBody, f"{{{namespace}}}component")
        section_component.append(element)

    # Create a new ElementTree with the result root
    refined_message = ET.ElementTree(refined_message_root)
    return ET.tostring(refined_message, encoding="unicode")


def _select_message_header(raw_message: bytes) -> bytes:
    """
    Helper function that selects the header of an incoming message.

    :param raw_message: The XML input.
    :return: The header section of the XML.
    """
    HEADER_SECTIONS = [
        "realmCode",
        "typeId",
        "templateId",
        "id",
        "code",
        "title",
        "effectiveTime",
        "confidentialityCode",
        "languageCode",
        "setId",
        "versionNumber",
        "recordTarget",
        "author",
        "custodian",
        "componentOf",
    ]

    # Set up XPath expression
    namespaces = {"hl7": "urn:hl7-org:v3"}
    xpath_expression = " | ".join(
        [f"//hl7:ClinicalDocument/hl7:{section}" for section in HEADER_SECTIONS]
    )
    # Use XPath to find elements matching the expression
    elements = raw_message.xpath(xpath_expression, namespaces=namespaces)

    # Create & set up a new root element for the refined XML
    header = ET.Element(raw_message.tag)

    # Append the filtered elements to the new root
    for element in elements:
        header.append(element)

    return header
