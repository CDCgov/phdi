from pathlib import Path
from typing import List

import requests
from dibbs.base_service import BaseService
from fastapi import Request
from fastapi import Response
from lxml import etree as ET

TCR_URL = "trigger-code-reference-service:8081"
TCR_ENDPOINT = TCR_URL + "/get-value-sets/?condition_code="

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

    if sections_to_include:
        sections_to_include, error_message = validate_sections_to_include(
            sections_to_include
        )

        if error_message != "":
            return Response(content=error_message, status_code=422)

        data = refine(validated_message, sections_to_include, conditions_to_include)

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


def _generate_clinical_xpaths(system: str, codes: List[str]) -> List[str]:
    """
    This is a small helper function that loops through codes to create a set of
    xpaths that can be used in the refine step.

    :param system: This is the system type of the clinical service codes.
    :param codes: This is a list of the clinical service codes for a specified
    SNOMED code.
    """
    """
    As of May 2024, these are the code systems used in clinical services
    code_system
    http://snomed.info/sct                         28102
    http://loinc.org                                9509
    http://hl7.org/fhir/sid/icd-10-cm               5892
    http://www.nlm.nih.gov/research/umls/rxnorm      468
    http://hl7.org/fhir/sid/cvx                        2
    """
    system_dict = {
        "http://hl7.org/fhir/sid/icd-10-cm": "ICD10",
        "http://snomed.info/sct": "SNOMED CT",
        "http://loinc.org": "LOINC",
        "http://www.nlm.nih.gov/research/umls/rxnorm": "?",  # TODO
        "http://hl7.org/fhir/sid/cvx": "?",  # TODO
    }
    # TODO: confirm vaccine and value xpaths with sample data
    # Loop through each code and create the XPath expressions
    return [
        xpath
        for code in codes
        for xpath in [
            f"//*[local-name()='code'][@code='{code}' and @codeSystemName='{system_dict.get(system, system)}']",
            f"//*[local-name()='vaccineCode'][@coding='{code}' and @codeSystemName='{system_dict.get(system, system)}']",
            f"//*[local-name()='value'][@code='{code}' and @codeSystemName='{system_dict.get(system, system)}']",
        ]
    ]


def get_clinical_services_to_include(condition_codes: str) -> List[str]:
    """
    This a function that loops through the provided condition codes. For each
    condition code provided, it calls the trigger-code-reference service to get
    the relevant clinical services for that condition. It then loops through
    each of those clinical service codes and their system to create an xpath
    query.

    :param condition_codes: SNOMED condition codes to look up in TCR service
    :return: List of xpath queries to check
    """
    conditions_list = condition_codes.split(",")
    clinical_services_to_include = []

    for condition in conditions_list:
        clinical_services = requests.get(TCR_ENDPOINT + condition)
        for system, entries in clinical_services.items():
            for entry in entries:
                system = entry.get("system")
                xpath_queries = _generate_clinical_xpaths(system, entry.get("codes"))
                clinical_services_to_include.extend(xpath_queries)
    return clinical_services_to_include


def refine(
    validated_message: bytes, sections_to_include: str, conditions_to_include: str
) -> str:
    """
    Refines an incoming XML message based on the sections to include.

    :param validated_message: The XML input.
    :param sections_to_include: The sections to include in the refined message.
    :param conditions_to_include: XPaths of clinical service codes.
    :return: The refined message.
    """
    header = select_message_header(validated_message)

    # Set up XPath expression
    # this namespace is only used for filtering
    namespaces = {"hl7": "urn:hl7-org:v3"}
    sections_xpath_expression = "or".join(
        [f"@code='{section}'" for section in sections_to_include]
    )

    if conditions_to_include:
        clinical_services_to_include = get_clinical_services_to_include(
            conditions_to_include
        )
        services_xpath_expression = " or ".join(clinical_services_to_include)
        xpath_expression = f"//*[local-name()='section'][hl7:code[{sections_xpath_expression}] and ({services_xpath_expression})]"
    else:
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
