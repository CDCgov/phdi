from pathlib import Path

import httpx
from dibbs.base_service import BaseService
from fastapi import Request
from fastapi import Response
from lxml import etree as ET

from app.config import get_settings
from app.utils import _generate_clinical_xpaths

settings = get_settings()
TCR_ENDPOINT = f"{settings['tcr_url']}/get-value-sets/?condition_code="

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
    refiner_input: Request,
    sections_to_include: str | None = None,
    conditions_to_include: str | None = None,
) -> Response:
    """
    Refines an incoming XML message based on the fields to include and whether
    to include headers.

    :param request: The request object containing the XML input.
    :param sections_to_include: The fields to include in the refined message.
    :param conditions_to_include: The SNOMED condition codes to search for
    and then include the relevant clinical services in the refined message.
    :return: The RefinerResponse which includes the `refined_message`
    """
    data = await refiner_input.body()

    validated_message, error_message = validate_message(data)
    if error_message != "":
        return Response(content=error_message, status_code=400)

    sections = None
    if sections_to_include:
        sections, error_message = validate_sections_to_include(sections_to_include)
        if error_message != "":
            return Response(content=error_message, status_code=422)

    clinical_services_xpaths = None
    if conditions_to_include:
        clinical_services = await get_clinical_services(conditions_to_include)
        if error_message != "":
            return Response(content=error_message, status_code=502)
        clinical_services_xpaths = create_clinical_xpaths(clinical_services)

    data = refine(validated_message, sections, clinical_services_xpaths)

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

    if sections_to_include is None:
        return (None, "")

    section_loincs = []
    sections = sections_to_include.split(",")
    for section in sections:
        if section not in section_LOINCs:
            section_loincs = None
            error_message = f"{section} is invalid. Please provide a valid section."
            break
        else:
            section_loincs.append(section)

    return (section_loincs, error_message)


async def get_clinical_services(condition_codes: str) -> tuple[list, str]:
    """
    This a function that loops through the provided condition codes. For each
    condition code provided, it calls the trigger-code-reference service to get
    the relevant clinical services for that condition.

    :param condition_codes: SNOMED condition codes to look up in TCR service
    :return: List of clinical_service dictionaries to check, error message
    """
    error_message = ""
    clinical_services_list = []
    conditions_list = condition_codes.split(",")
    async with httpx.AsyncClient() as client:
        for condition in conditions_list:
            response = await client.get(TCR_ENDPOINT + condition)
            clinical_services = response.json()
            match response.status_code:
                case 200:
                    clinical_services_list.append(clinical_services)
                case _:  # 400/422/404 cases should return empty list, errors
                    return ([], response)
    return (clinical_services_list, error_message)


def create_clinical_xpaths(clinical_services_list: list[dict]) -> list[str]:
    """
    This function loops through each of those clinical service codes and their
    system to create a list of all possible xpath queries.
    :param clinical_services_list: List of clinical_service dictionaries.
    :return: List of xpath queries to check.
    """
    clinical_services_xpaths = []
    for clinical_services in clinical_services_list:
        for system, entries in clinical_services.items():
            for entry in entries:
                system = entry.get("system")
                xpaths = _generate_clinical_xpaths(system, entry.get("codes"))
                clinical_services_xpaths.extend(xpaths)
    return clinical_services_xpaths


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
    :param clinical_services_xpaths: clinical service XPaths to include in the
    refined message.
    :return: The refined message.
    """
    header = select_message_header(validated_message)

    # Set up XPath expressions
    namespaces = {"hl7": "urn:hl7-org:v3"}
    if sections_to_include:
        sections_xpaths = " or ".join(
            [f"@code='{section}'" for section in sections_to_include]
        )
        sections_xpath_expression = (
            f"//*[local-name()='section'][hl7:code[{sections_xpaths}]]"
        )

    if clinical_services:
        services_xpath_expression = " | ".join(clinical_services)

    # both are handled slightly differently
    if sections_to_include and clinical_services:
        elements = []
        sections = validated_message.xpath(
            sections_xpath_expression, namespaces=namespaces
        )
        for section in sections:
            condition_elements = section.xpath(
                services_xpath_expression, namespaces=namespaces
            )
            if condition_elements:
                elements.extend(condition_elements)
        return add_root_element(header, elements)

    if sections_to_include:
        xpath_expression = sections_xpath_expression
    elif clinical_services:
        xpath_expression = services_xpath_expression
    else:
        xpath_expression = "//*[local-name()='section']"
    elements = validated_message.xpath(xpath_expression, namespaces=namespaces)
    return add_root_element(header, elements)


def add_root_element(header: bytes, elements: list) -> str:
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
