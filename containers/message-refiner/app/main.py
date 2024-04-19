from pathlib import Path

from dibbs.base_service import BaseService
from fastapi import Request
from fastapi import Response

MESSAGE_SECTIONS = {
    "10164-2": "HISTORY OF PRESENT ILLNESS",
    "11369-6": "History of Immunization Narrative",
    "29549-3": "MEDICATIONS ADMINISTERED",
    "18776-5": "Plan of care note",
    "11450-4": "Problem list - Reported",
    "29299-5": "REASON FOR VISIT",
    "30954-2": "Relevant diagnostic tests/laboratory data Narrative",
    "29762-2": "Social history Narrative",
    "46240-8": "History of Hospitalizations+Outpatient visits Narrative",
}


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
        # TODO: add logic to filter the XML message based on the sections_to_include
        refined_message = Response(content=data, media_type="application/xml")
    else:
        refined_message = Response(content=data, media_type="application/xml")

    return refined_message


def validate_sections_to_include(sections_to_include: str | None) -> list:
    """
    Validates the sections to include in the refined message.

    :param sections_to_include: The sections to include in the refined message.
    :return: The sections to include in the refined message as a list
    """
    if sections_to_include:
        sections = sections_to_include.split(",")
        for section in sections:
            if section not in [
                "social-history",
                "medications",
            ]:
                raise ValueError("Invalid section to include.")
    return sections_to_include


def refine():
    # Parse XML
    with open(
        "C://Repos/phdi/containers/message-refiner/tests/assets/CDA_eICR_LAC.xml",
        # ("C://Repos/phdi/containers/message-parser/assets/demo_phdc.xml"),
        "r",
    ) as file:
        xml_string = file.read()
        # parser = ET.XMLParser(remove_blank_text=True)
        # tree = ET.parse(
        #     file,
        #     parser,
        # )

    # Parse the XML string into an ElementTree
    root = ET.fromstring(xml_string)

    # Define the namespace dictionary for XPath queries
    ns = {"ns0": "urn:hl7-org:v3"}

    # Define the XPath expression to select elements before the first component,social history, and encounter details
    xpath_expr = "//*[not(preceding-sibling::ns0:component)] | //ns0:socialHistory | //ns0:encounterDetails"

    # Use XPath to find elements matching the expression
    elements = root.xpath(xpath_expr, namespaces=ns)

    # Create a new root element for the filtered XML
    filtered_root = ET.Element(root.tag)

    # Append the filtered elements to the new root
    for element in elements:
        filtered_root.append(element)

    # Serialize the filtered XML to a string
    # filtered_xml_str = ET.tostring(filtered_root, encoding="unicode")

    # Create a new ElementTree with the result root
    filtered_tree = ET.ElementTree(filtered_root)

    # Print the result as XML
    filtered_tree.write("C://Repos/phdi/result.xml")
