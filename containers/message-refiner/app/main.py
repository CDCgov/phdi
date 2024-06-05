from pathlib import Path
from typing import Annotated

import httpx
from dibbs.base_service import BaseService
from fastapi import Query
from fastapi import Request
from fastapi import Response
from fastapi import status
from fastapi.openapi.utils import get_openapi
from fastapi.responses import FileResponse
from lxml import etree as ET

from app.config import get_settings
from app.models import RefineECRResponse
from app.utils import _generate_clinical_xpaths
from app.utils import read_json_from_assets

settings = get_settings()
TCR_ENDPOINT = f"{settings['tcr_url']}/get-value-sets?condition_code="


# LOINC codes for the required sections of an eICR
SECTION_LOINCS = [
    "46240-8",  # encounters: hospitalizations+outpatient visits narrative
    "10164-2",  # history of present illness
    "29549-3",  # medications administered
    "18776-5",  # plan of treatment: care plan
    "11450-4",  # problem: reported list
    "29299-5",  # reason for visit
    "30954-2",  # results: diagnostic tests/laboratory data narrative
    "29762-2",  # social history: narrative
]

# dictionary of the section's LOINC, displayName, OID, and title
SECTION_DETAILS = {
    "46240-8": (
        "History of encounters",
        "2.16.840.1.113883.10.20.22.2.22.1",
        "2015-08-01",
        "Encounters",
    ),
    "10164-2": (
        "History of Present Illness",
        "2.16.840.1.113883.10.20.22.2.20",
        "2015-08-01",
        "History of Present Illness",
    ),
    "29549-3": (
        "Medications Administered",
        "2.16.840.1.113883.10.20.22.2.38",
        "2014-06-09",
        "Medications Administered",
    ),
    "18776-5": (
        "Plan of Treatment",
        "2.16.840.1.113883.10.20.22.2.10",
        "2014-06-09",
        "Plan of Treatment",
    ),
    "11450-4": (
        "Problem List",
        "2.16.840.1.113883.10.20.22.2.5.1",
        "2015-08-01",
        "Problem List",
    ),
    "29299-5": (
        "Reason For Visit",
        "2.16.840.1.113883.10.20.22.2.12",
        "2015-08-01",
        "Reason For Visit",
    ),
    "30954-2": (
        "Relevant diagnostic tests and/or laboratory data",
        "2.16.840.1.113883.10.20.22.2.3.1",
        "2015-08-01",
        "Results",
    ),
    "29762-2": (
        "Social History",
        "2.16.840.1.113883.10.20.22.2.17",
        "2015-08-01",
        "Social History",
    ),
}

# Instantiate FastAPI via DIBBs' BaseService class
app = BaseService(
    service_name="Message Refiner",
    service_path="/message-refiner",
    description_path=Path(__file__).parent.parent / "description.md",
    include_health_check_endpoint=False,
).start()


# /ecr endpoint request examples
refine_ecr_request_examples = read_json_from_assets("sample_refine_ecr_request.json")
refine_ecr_response_examples = read_json_from_assets("sample_refine_ecr_response.json")


def custom_openapi():
    """
    This customizes the FastAPI response to allow example requests given that the
    raw Request cannot have annotations.
    """
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    path = openapi_schema["paths"]["/ecr"]["post"]
    path["requestBody"] = {
        "content": {
            "application/xml": {
                "schema": {"type": "Raw eCR XML payload"},
                "examples": refine_ecr_request_examples,
            }
        }
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/")
async def health_check():
    """
    Check service status. If an HTTP 200 status code is returned along with
    '{"status": "OK"}' then the refiner service is available and running
    properly.
    """
    return {"status": "OK"}


@app.get("/example-collection")
async def get_uat_collection() -> FileResponse:
    """
    Fetches a Postman Collection of sample requests designed for UAT.
    The Collection is a JSON-exported file consisting of five GET and POST
    requests to endpoints of the publicly available dibbs.cloud server.
    The requests showcase the functionality of various aspects of the TCR
    and the message refine.
    """
    uat_collection_path = (
        Path(__file__).parent.parent
        / "assets"
        / "Message_Refiner_UAT.postman_collection.json"
    )
    return FileResponse(uat_collection_path)


@app.post(
    "/ecr",
    response_model=RefineECRResponse,
    status_code=200,
    responses=refine_ecr_response_examples,
)
async def refine_ecr(
    refiner_input: Request,
    sections_to_include: Annotated[
        str | None,
        Query(
            description="""The sections of an ECR to include in the refined message.
            Multiples can be delimited by a comma. Valid LOINC codes for sections are:\n
            46240-8: Encounters--Hospitalizations+outpatient visits narrative\n
            10164-2: History of present illness\n
            29549-3: Medications administered\n
            18776-5: Plan of treatment: Care plan\n
            11450-4: Problem--Reported list\n
            29299-5: Reason for visit\n
            30954-2: Results--Diagnostic tests/laboratory data narrative\n
            29762-2: Social history--Narrative\n
            """
        ),
    ] = None,
    conditions_to_include: Annotated[
        str | None,
        Query(
            description="The SNOMED condition codes to use to search for relevant clinical services in the ECR."
            + " Multiples can be delimited by a comma."
        ),
    ] = None,
) -> Response:
    """
    Refines an incoming XML ECR message based on sections to include and/or trigger code
    conditions to include, based on the parameters included in the endpoint.

    The return will be a formatted, refined XML, limited to just the data specified.

    :param refiner_input: The request object containing the XML input.
    :param sections_to_include: The fields to include in the refined message.
    :param conditions_to_include: The SNOMED condition codes to use to search for
    relevant clinical services in the ECR.
    :return: The RefineECRResponse, the refined XML as a string.
    """
    data = await refiner_input.body()

    validated_message, error_message = validate_message(data)
    if error_message:
        return Response(content=error_message, status_code=status.HTTP_400_BAD_REQUEST)

    sections = None
    if sections_to_include:
        sections, error_message = validate_sections_to_include(sections_to_include)
        if error_message:
            return Response(
                content=error_message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

    clinical_services_xpaths = None
    if conditions_to_include:
        responses = await get_clinical_services(conditions_to_include)
        # confirm all API responses were 200
        if set([response.status_code for response in responses]) != {200}:
            error_message = ";".join(
                [str(response) for response in responses if response.status_code != 200]
            )
            return Response(
                content=error_message, status_code=status.HTTP_502_BAD_GATEWAY
            )
        clinical_services = [response.json() for response in responses]
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


async def get_clinical_services(condition_codes: str) -> list[dict]:
    """
    This a function that loops through the provided condition codes. For each
    condition code provided, it calls the trigger-code-reference service to get
    the API response for that condition.

    :param condition_codes: SNOMED condition codes to look up in TCR service
    :return: List of API responses to check
    """
    clinical_services_list = []
    conditions_list = condition_codes.split(",")
    async with httpx.AsyncClient() as client:
        for condition in conditions_list:
            response = await client.get(TCR_ENDPOINT + condition)
            clinical_services_list.append(response)
    return clinical_services_list


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
    :param clinical_services: clinical service XPaths to include in the
    refined message.
    :return: The refined message.
    """
    header = select_message_header(validated_message)
    namespaces = {"hl7": "urn:hl7-org:v3"}
    elements = []

    # if no parameters are provided, return the header with all sections
    if not sections_to_include and not clinical_services:
        xpath_expression = "//*[local-name()='section']"
        elements = validated_message.xpath(xpath_expression, namespaces=namespaces)
        return add_root_element(header, elements)

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
    # for the sections not included
    if sections_to_include and not clinical_services:
        minimal_sections = create_minimal_sections(sections_to_include)
        xpath_expression = sections_xpath_expression
        elements = validated_message.xpath(xpath_expression, namespaces=namespaces)
        return add_root_element(header, elements + minimal_sections)

    # if we only have clinical_services then we use the unique sections from the
    # services_section_and_elements dictionary to include entries to sections + minimal sections
    # if no sections_to_include are provided
    if clinical_services and not sections_to_include:
        elements = []
        for section_code, entries in services_section_and_elements.items():
            minimal_section = create_minimal_section(section_code, empty_section=False)
            for entry in entries:
                minimal_section.append(entry)
            elements.append(minimal_section)
        minimal_sections = create_minimal_sections(
            sections_with_conditions=services_section_and_elements.keys(),
            empty_section=True,
        )
        return add_root_element(header, elements + minimal_sections)

    # if we have both sections_to_include and clinical_services then we need to
    # prioritize the sections_to_include and remove any sections that overlap;
    # then we need to add the remaining clinical_services to their parent sections,
    # and create minimal sections for any remaining sections
    if sections_to_include and clinical_services:
        # check if there is match between sections_to_include and conditions  we want to include
        # if there is a match, these are the _only_ sections we want to include
        matching_sections = set(sections_to_include) & set(
            services_section_and_elements.keys()
        )
        # if there is no match, we will respond with empty; minimal sections
        if not matching_sections:
            minimal_sections = create_minimal_sections()
            return add_root_element(header, minimal_sections)

        elements = []
        for section_code in matching_sections:
            minimal_section = create_minimal_section(section_code, empty_section=False)
            for entry in services_section_and_elements[section_code]:
                minimal_section.append(entry)
            elements.append(minimal_section)

        minimal_sections = create_minimal_sections(
            sections_with_conditions=matching_sections,
            empty_section=True,
        )

        return add_root_element(header, elements + minimal_sections)


def create_minimal_section(section_code: str, empty_section: bool) -> ET.Element:
    """
    Creates a minimal section element based on the LOINC section code.

    :param section_code: The LOINC code of the section to create a minimal section for.
    :param empty_section: Whether the section should be empty and include a nullFlavor attribute.
    :return: A minimal section element or None if the section code is not recognized.
    """
    if section_code not in SECTION_DETAILS:
        return None

    display_name, template_root, template_extension, title_text = SECTION_DETAILS[
        section_code
    ]

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


def create_minimal_sections(
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
        minimal_section = create_minimal_section(section_code, empty_section)
        if minimal_section:
            minimal_sections.append(minimal_section)
    return minimal_sections


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
    Validates that an incoming XML message can be parsed by lxml's ET .

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
