from pathlib import Path

from dibbs.base_service import BaseService
from fastapi import Request
from fastapi import Response
from lxml import etree as ET

# Instantiate FastAPI via DIBBs' BaseService class
app = BaseService(
    service_name="Message Refiner",
    service_path="/message-refiner",
    description_path=Path(__file__).parent.parent / "description.md",
    include_health_check_endpoint=False,
).start()


@app.get("/")
async def health_check():
    """
    Check service status. If an HTTP 200 status code is returned along with
    '{"status": "OK"}' then the refiner service is available and running
    properly.
    """
    return {"status": "OK"}


@app.post("/ecr/")
async def refine_ecr(
    refiner_input: Request, sections_to_include: str | None = None
) -> Response:
    """
    Refines an incoming XML message based on the fields to include and whether
    to include headers.

    :param request: The request object containing the XML input.
    :param fields_to_include: The fields to include in the refined message.
    :return: The RefinerResponse which includes the `refined_message`
    """
    data = await refiner_input.body()

    validated_message, error_message = validate_message(data)
    if error_message != "":
        return Response(content=error_message, status_code=400)

    if sections_to_include:
        sections_to_include, error_message = validate_sections_to_include(
            sections_to_include
        )

        if error_message != "":
            return Response(content=error_message, status_code=422)

        data = refine(validated_message, sections_to_include)

    return Response(content=data, media_type="application/xml")


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
    section_LOINCs = [
        "10164-2",  # history of present illness
        "11369-6",  # history of immunization narrative
        "29549-3",  # medications administered
        "18776-5",  # plan of care note
        "11450-4",  # problem list - reported
        "29299-5",  # reason for visit
        "30954-2",  # relevant diagnostic tests/laboratory data narrative
        "29762-2",  # social history narrative
        "46240-8",  # history of hospitalizations+outpatient visits narrative
    ]

    error_message = ""
    section_loincs = []

    if sections_to_include:
        section_loincs = []
        sections = sections_to_include.split(",")
        for section in sections:
            if section not in section_LOINCs:
                section_loincs = None
                error_message = f"{section} is invalid. Please provide a valid section."
                break
            else:
                section_loincs.append(section)

    return (section_loincs, error_message) if section_loincs else (None, error_message)


def refine(validated_message: bytes, sections_to_include: str) -> str:
    """
    Refines an incoming XML message based on the sections to include.

    :param validated_message: The XML input.
    :param sections_to_include: The sections to include in the refined message.
    :return: The refined message.
    """
    header = select_message_header(validated_message)

    # Set up XPath expression
    # this namespace is only used for filtering
    namespaces = {"hl7": "urn:hl7-org:v3"}
    sections_xpath_expression = "or".join(
        [f"@code='{section}'" for section in sections_to_include]
    )
    xpath_expression = (
        f"//*[local-name()='section'][hl7:code[{sections_xpath_expression}]]"
    )

    # Use XPath to find elements matching the expression
    elements = validated_message.xpath(xpath_expression, namespaces=namespaces)

    # Create & set up a new root element for the refined XML
    # we are using a combination of a direct namespace uri and nsmap so that we can
    # ensure that the default namespaces are set correctly
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


def select_message_header(raw_message: bytes) -> bytes:
    """
    Selects the header of an incoming message.

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
