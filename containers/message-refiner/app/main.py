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

    if sections_to_include:
        refined_data = refine(data, sections_to_include)
        refined_message = Response(content=refined_data, media_type="application/xml")
    else:
        refined_message = Response(content=data, media_type="application/xml")

    return refined_message


def validate_sections_to_include(sections_to_include: str | None) -> list:
    """
    Validates the sections to include in the refined message and returns them as a list
    of corresponding LOINC codes.

    :param sections_to_include: The sections to include in the refined message.
    :return: The sections to include in the refined message as a list of LOINC codes
    corresponding to the sections.
    """
    section_LOINCs = {
        "history of present illness": "10164-2",
        "history of immunization narrative": "11369-6",
        "medications administered": "29549-3",
        "plan of care note": "18776-5",
        "problem list - reported": "11450-4",
        "reason for visit": "29299-5",
        "relevant diagnostic tests/laboratory data narrative": "30954-2",
        "social history narrative": "29762-2",
        "history of hospitalizations+outpatient visits narrative": "46240-8",
    }
    section_loincs = None
    if sections_to_include:
        sections = sections_to_include.split(",")
        section_loincs = []
        for section in sections:
            if section not in section_LOINCs.keys():
                raise ValueError(
                    f"{section} is invalid. Please provide a valid section."
                )

            else:
                section_loincs.append(section_LOINCs[section.lower()])

    return section_loincs


def refine(raw_message: bytes, sections_to_include: str | None = None) -> bytes:
    """
    Refines an incoming XML message based on the sections to include.

    :param raw_message: The XML input.
    :param sections_to_include: The sections to include in the refined message.
    :return: The refined message.
    """

    if sections_to_include is None:
        return raw_message
    else:
        raw_message = ET.fromstring(raw_message)

        # Validate sections to include
        sections = validate_sections_to_include(sections_to_include)

        # Set up XPath expression
        namespaces = {"hl7": "urn:hl7-org:v3"}
        sections_xpath_expression = "or".join(
            [f"@code='{section}'" for section in sections]
        )
        xpath_expression = (
            f"//*[local-name()='section'][hl7:code[{sections_xpath_expression}]]"
        )
        # print("xpath_expr: ", xpath_expression)

        # Use XPath to find elements matching the expression
        elements = raw_message.xpath(xpath_expression, namespaces=namespaces)
        # print("len(elements): ", len(elements))

        # Create & set up a new root element for the refined XML
        refined_message_root = ET.Element(raw_message.tag)
        component = ET.Element("component")
        structuredBody = ET.Element("structuredBody")

        # Append the filtered elements to the new root
        for element in elements:
            c = ET.Element("component")
            c.append(element)
            structuredBody.append(c)
        component.append(structuredBody)
        refined_message_root.append(component)

        # Create a new ElementTree with the result root
        refined_message = ET.ElementTree(refined_message_root)
        return refined_message
