from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from lxml import etree

# read json that contains details for refining and is the base of what drives `refine`
from app.utils import read_json_from_assets

REFINER_DETAILS = read_json_from_assets("refiner_details.json")

# extract section LOINC codes from the REFINER_DETAILS dictionary
SECTION_LOINCS = list(REFINER_DETAILS["sections"].keys())

# ready to use list of all trigger code templateIds for simpler XPath query construction
TRIGGER_CODE_TEMPLATE_IDS = [
    "2.16.840.1.113883.10.20.15.2.3.5",
    "2.16.840.1.113883.10.20.15.2.3.3",
    "2.16.840.1.113883.10.20.15.2.3.4",
    "2.16.840.1.113883.10.20.15.2.3.2",
]


def validate_message(raw_message: str) -> tuple[bytes | None, str]:
    """
    Validates that an incoming XML message can be parsed by lxml's etree.

    :param raw_message: The XML input.
    :return: The validation result as a string.
    """
    error_message = ""
    try:
        validated_message = etree.fromstring(raw_message)
        return (validated_message, error_message)
    except etree.XMLSyntaxError as error:
        error_message = f"XMLSyntaxError: {error}"
        return (None, str(error_message))


def validate_sections_to_include(sections_to_include: str | None) -> tuple[list, str]:
    """
    Validates the sections to include in the refined message and returns them as a list
    of corresponding LOINC codes.

    :param sections_to_include: The sections to include in the refined message.
    :raises ValueError: When at least one of the sections_to_include is invalid.
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
    validated_message: etree.Element,
    sections_to_include: Optional[List[str]] = None,
    clinical_services: Optional[Dict[str, List[str]]] = None,
) -> str:
    """
    Refines an eICR XML document by processing its sections based on the provided parameters.

    Case 1: No parameters (only validated_message provided)
        - Check for template IDs.
        - If found, find matching observations, clean up entries, and update text.
        - If not found, create a minimal section.

    Case 2: sections_to_include provided
        - For sections in sections_to_include:
            - Ignore processing (leave them as they are, unprocessed).
        - For all other sections:
            - Check for template IDs.
            - If found, find matching observations, clean up entries, and update text.
            - If not found, create a minimal section.

    Case 3: clinical_services provided
        - Check for both template IDs and codes.
        - If found, find matching observations, clean up entries, and update text.
        - If not found, create a minimal section.

    Case 4: Both sections_to_include and clinical_services provided
        - For sections in sections_to_include:
            - Check for both template IDs and codes.
            - If found, find matching observations, clean up entries, and update text.
            - If not found, create a minimal section.
        - For all other sections:
            - Check for template IDs.
            - If found, find matching observations, clean up entries, and update text.
            - If not found, create a minimal section.

    :param validated_message: The eICR XML document to be refined.
    :param sections_to_include: Optional list of section LOINC codes for the sections from
        the <structuredBody>; passing only this parameter retains those section whereas
        passing it with clinical_services focuses the search to the sections in this list.
    :param clinical_services: Optional dictionary of clinical service codes to check within
        sections from the Trigger Code Reference Service.
    :return: The refined eICR XML document as a string.
    """
    # dictionary that will hold the section processing instructions
    # this is based on the combination of parameters passed to `refine`
    # as well as deails from REFINER_DETAILS
    section_processing = {
        code: details for code, details in REFINER_DETAILS["sections"].items()
    }

    namespaces = {"hl7": "urn:hl7-org:v3"}
    structured_body = validated_message.find(".//hl7:structuredBody", namespaces)

    # case 2: if only sections_to_include is provided, remove these sections from section_processing
    if sections_to_include is not None and clinical_services is None:
        section_processing = {
            key: value
            for key, value in section_processing.items()
            if key not in sections_to_include
        }

    # process sections
    for code, details in section_processing.items():
        section = _get_section_by_code(structured_body, code)
        if section is None:
            continue  # go to the next section if not found

        # case 4: search in sections_to_include for clinical_services; for sections
        # not in sections_to_include, search for templateIds
        if sections_to_include is not None and clinical_services is not None:
            if code in sections_to_include:
                combined_xpaths = _generate_combined_xpath(
                    template_ids=TRIGGER_CODE_TEMPLATE_IDS,
                    clinical_services_dict=clinical_services,
                )
                clinical_services_codes = [
                    code for codes in clinical_services.values() for code in codes
                ]
                _process_section(
                    section,
                    combined_xpaths,
                    namespaces,
                    TRIGGER_CODE_TEMPLATE_IDS,
                    clinical_services_codes,
                )
            else:
                combined_xpaths = _generate_combined_xpath(
                    template_ids=TRIGGER_CODE_TEMPLATE_IDS,
                    clinical_services_dict={},
                )
                _process_section(
                    section, combined_xpaths, namespaces, TRIGGER_CODE_TEMPLATE_IDS
                )

        # case 3: process all sections with clinical_services (no sections_to_include)
        elif clinical_services is not None and sections_to_include is None:
            combined_xpaths = _generate_combined_xpath(
                template_ids=TRIGGER_CODE_TEMPLATE_IDS,
                clinical_services_dict=clinical_services,
            )
            clinical_services_codes = [
                code for codes in clinical_services.values() for code in codes
            ]
            _process_section(
                section,
                combined_xpaths,
                namespaces,
                TRIGGER_CODE_TEMPLATE_IDS,
                clinical_services_codes,
            )

        # case 1: no parameters, process all sections normally
        # case 2: process sections not in sections_to_include
        else:
            combined_xpaths = _generate_combined_xpath(
                template_ids=TRIGGER_CODE_TEMPLATE_IDS, clinical_services_dict={}
            )
            _process_section(
                section, combined_xpaths, namespaces, TRIGGER_CODE_TEMPLATE_IDS
            )

    # TODO: there may be sections that are not standard but appear in an eICR that
    # we could either decide to add to the refiner_details.json or use this code
    # before returning the refined output that removes sections that are not required
    for section in structured_body.findall(".//hl7:section", namespaces):
        section_code = section.find(".//hl7:code", namespaces).get("code")
        if section_code not in SECTION_LOINCS:
            parent = section.getparent()
            parent.remove(section)

    return etree.tostring(validated_message, encoding="unicode")


def _process_section(
    section: etree.Element,
    combined_xpaths: str,
    namespaces: dict,
    template_ids: List[str],
    clinical_services_codes: Optional[List[str]] = None,
) -> None:
    """
    Processes a section by checking for elements, finding observations,
    cleaning up entries, and updating text.

    :param section: The section element to process.
    :param combined_xpaths: The combined XPath expression for finding elements.
    :param namespaces: The namespaces to use in XPath queries.
    :param template_ids: The list of template IDs to check.
    :param clinical_services_codes: Optional list of clinical service codes to check.
    """
    check_elements = _are_elements_present(
        section, "templateId", template_ids, namespaces
    )
    if clinical_services_codes:
        check_elements |= _are_elements_present(
            section, "code", clinical_services_codes, namespaces
        )

    if check_elements:
        observations = _get_observations(section, combined_xpaths, namespaces)
        if observations:
            paths = [_find_path_to_entry(obs) for obs in observations]
            _prune_unwanted_siblings(paths, observations)
            _update_text_element(section, observations)
        else:
            _create_minimal_section(section)
    else:
        _create_minimal_section(section)


def _generate_combined_xpath(
    template_ids: List[str], clinical_services_dict: Dict[str, List[str]]
) -> str:
    """
    Generate a combined XPath expression for templateIds and all codes across all systems, ensuring they are within 'observation' elements.
    """
    xpath_conditions = []

    # add templateId conditions within <observation> elements if needed
    if template_ids:
        template_id_conditions = [
            f'.//hl7:observation[hl7:templateId[@root="{tid}"]]' for tid in template_ids
        ]
        xpath_conditions.extend(template_id_conditions)

    # add code conditions within <observation> elements
    for codes in clinical_services_dict.values():
        for code in codes:
            code_conditions = f'.//hl7:observation[hl7:code[@code="{code}"]]'
            xpath_conditions.append(code_conditions)

    # combine all conditions into a single XPath query using the union operator
    combined_xpath = " | ".join(xpath_conditions)
    return combined_xpath


def _get_section_by_code(
    structured_body: etree.Element,
    code: str,
    namespaces: dict = {"hl7": "urn:hl7-org:v3"},
) -> etree.Element:
    """
    Gets a section of an eICR's <structuredBody> by its LOINC code and returns the <section> element.

    :param structuredBody: The structuredBody element to search within.
    :param code: LOINC code of the <section> to retrieve.
    :param namespaces: The namespaces to use when searching for elements and defaults to 'hl7'.
    :return: The <section> element of the section with the given LOINC code.
    """
    xpath_query = f'.//hl7:section[hl7:code[@code="{code}"]]'
    section = structured_body.xpath(xpath_query, namespaces=namespaces)
    if section is not None and len(section) == 1:
        return section[0]


def _get_entries_for_section(
    section: Union[etree.Element, Callable[..., etree.Element]],
    namespaces: dict = {"hl7": "urn:hl7-org:v3"},
    *args,
    **kwargs,
) -> List[etree.Element]:
    """
    Gets the entries of a section of an eICR and returns a list of <entry> elements.

    :param section: The <section> element of the section to retrieve entries from or a function that returns the section.
    :param namespaces: The namespaces to use when searching for elements and defaults to 'hl7'.
    :param args: Additional arguments to pass to the callable if `section` is a callable.
    :param kwargs: Additional keyword arguments to pass to the callable if `section` is a callable.
    :return: A list of <entry> elements of the entries in the section.
    """
    if callable(section):
        section = section(*args, **kwargs)

    entries = section.xpath(".//hl7:entry", namespaces=namespaces)
    if entries is not None:
        return entries


def _get_observations(
    section: Union[etree.Element, Callable[..., etree.Element]],
    combined_xpath: str,
    namespaces: dict = {"hl7": "urn:hl7-org:v3"},
    *args,
    **kwargs,
) -> List[etree.Element]:
    """
    Get matching observations from a section or a callable returning a section based on combined XPath query.

    :param section: The <section> element of the section to retrieve entries from or a function that returns the section.
    :param combined_xpath: this will be either code values from the TCR or templateId root values in one combined XPath
    :param namespaces: The namespaces to use when searching for elements and defaults to 'hl7'.
    :param
    """
    if callable(section):
        section = section(*args, **kwargs)

    # use a list to store the final list of matching observation elements
    observations = []
    # use a set to store elements for uniqueness; trigger code data _may_ match clinical services
    seen = set()

    # search once for matching elements using the combined XPath expression
    matching_elements = section.xpath(combined_xpath, namespaces=namespaces)
    for elem in matching_elements:
        if elem not in seen:
            seen.add(elem)
            observations.append(elem)

    # TODO: we are not currently checking the codeSystemName at this time. this is because
    # there is variation even within a single eICR in connection to the codeSystemName.
    # you may see both "LOINC" and "loinc.org" as well as "SNOMED" and "SNOMED CT" in the
    # same message. dynamically altering the XPath with variant names adds complexity and computation;
    # we _can_ post filter, which i would suggest as a function that uses this one as its input.
    # this is why there are two main transformations of the response from the TCR; one that is a dictionary
    # of code systems and codes and another that is a combined XPath for all codes. this way we
    # loop less, search less, and aim for simplicity

    return observations


def _are_elements_present(
    section: Union[etree.Element, Callable[..., etree.Element]],
    search_type: str,
    search_values: List[str],
    namespaces: dict = {"hl7": "urn:hl7-org:v3"},
    *args,
    **kwargs,
) -> bool:
    """
    Checks if any of the specified elements are present in a section based on the search type and values.

    :param section: The <section> element of the section to search within or a function that returns such a section.
    :param search_type: The type of search ('templateId' or 'code').
    :param search_values: The list of values to search for (template IDs or codes).
    :param namespaces: The namespaces to use when searching for elements and defaults to 'hl7'.
    :param args: Additional arguments to pass to the callable if `section` is a callable.
    :param kwargs: Additional keyword arguments to pass to the callable if `section` is a callable.
    :return: True if any of the specified elements are present, False otherwise.
    """
    if callable(section):
        section = section(*args, **kwargs)

    if search_type == "templateId":
        xpath_queries = [
            f'.//hl7:templateId[@root="{value}"]' for value in search_values
        ]
    elif search_type == "code":
        xpath_queries = [f'.//hl7:code[@code="{value}"]' for value in search_values]

    combined_xpath = " | ".join(xpath_queries)
    return bool(section.xpath(combined_xpath, namespaces=namespaces))


def _find_path_to_entry(element: etree.Element) -> List[etree.Element]:
    """
    Helper function to find the path from a given element to the parent <entry> element.
    """
    path = []
    current_element = element
    while current_element.tag != "{urn:hl7-org:v3}entry":
        path.append(current_element)
        current_element = current_element.getparent()
        if current_element is None:
            raise ValueError("Parent <entry> element not found.")
    path.append(current_element)  # Add the <entry> element
    path.reverse()  # Reverse to get the path from <entry> to the given element
    return path


def _prune_unwanted_siblings(
    paths: List[List[etree.Element]], desired_elements: List[etree.Element]
):
    """
    Prunes unwanted siblings based on the desired elements.

    :param paths: List of paths, where each path is a list of elements from <entry> to an <observation>.
    :param desired_elements: List of desired <observation> elements to keep.
    """
    # flatten the list of paths and remove duplicates
    all_elements_to_keep = {elem for path in paths for elem in path}

    # iterate through all collected paths to prune siblings
    for path in paths:
        for element in path:
            parent = element.getparent()
            if parent is not None:
                siblings = parent.findall(element.tag)
                for sibling in siblings:
                    # only remove siblings that are not in the collected elements
                    if sibling not in all_elements_to_keep:
                        parent.remove(sibling)


def _extract_observation_data(
    observation: etree.Element,
) -> Dict[str, Union[str, bool]]:
    """
    Extracts relevant data from an observation element, including checking for trigger code template ID.

    :param observation: The observation element.
    :return: A dictionary with extracted data.
    """
    template_id_elements = observation.findall(
        ".//hl7:templateId", namespaces={"hl7": "urn:hl7-org:v3"}
    )
    is_trigger_code = False

    for elem in template_id_elements:
        root = elem.get("root")
        if root in TRIGGER_CODE_TEMPLATE_IDS:
            is_trigger_code = True
            break

    data = {
        "display_text": observation.find(
            ".//hl7:code", namespaces={"hl7": "urn:hl7-org:v3"}
        ).get("displayName"),
        "code": observation.find(
            ".//hl7:code", namespaces={"hl7": "urn:hl7-org:v3"}
        ).get("code"),
        "code_system": observation.find(
            ".//hl7:code", namespaces={"hl7": "urn:hl7-org:v3"}
        ).get("codeSystemName"),
        "is_trigger_code": is_trigger_code,
    }
    return data


def _create_or_update_text_element(observations: List[etree.Element]) -> etree.Element:
    """
    Creates or updates a <text> element with a table containing information from the given observations.

    :param section: The section element to update.
    :param observations: A list of observation elements.
    :return: The created or updated <text> element.
    """
    text_element = etree.Element("{urn:hl7-org:v3}text")
    title = etree.SubElement(text_element, "title")
    title.text = "Output from CDC PRIME DIBBs `message-refiner` API by request of STLT"

    table_element = etree.SubElement(text_element, "table", border="1")
    header_row = etree.SubElement(table_element, "tr")
    headers = ["Display Text", "Code", "Code System", "Trigger Code Observation"]

    for header in headers:
        th = etree.SubElement(header_row, "th")
        th.text = header

    # add observation data to table
    for observation in observations:
        data = _extract_observation_data(observation)
        row = etree.SubElement(table_element, "tr")
        for key in headers[:-1]:  # Exclude the last header as it's for the boolean flag
            td = etree.SubElement(row, "td")
            td.text = data[key.lower().replace(" ", "_")]

        # add boolean flag for trigger code observation
        td = etree.SubElement(row, "td")
        td.text = "TRUE" if data["is_trigger_code"] else "FALSE"

    return text_element


def _update_text_element(
    section: etree.Element, observations: List[etree.Element]
) -> None:
    """
    Updates the <text> element of a section to include information from observations.

    :param section: The section element containing the <text> element to update.
    :param observations: A list of observation elements to include in the <text> element.
    """
    new_text_element = _create_or_update_text_element(observations)

    existing_text_element = section.find(
        ".//hl7:text", namespaces={"hl7": "urn:hl7-org:v3"}
    )

    if existing_text_element is not None:
        section.replace(existing_text_element, new_text_element)
    else:
        section.insert(0, new_text_element)


def _create_minimal_section(section: etree.Element) -> None:
    """
    Creates a minimal section by updating the <text> element, removing all <entry> elements,
    and adding nullFlavor="NI" to the <section> element.

    :param section: The section element to update.
    """
    namespaces = {"hl7": "urn:hl7-org:v3"}
    text_element = section.find(".//hl7:text", namespaces=namespaces)

    if text_element is None:
        text_element = etree.Element("{urn:hl7-org:v3}text")
        section.append(text_element)

    # update the <text> element with the specific message
    text_element.clear()
    title_element = etree.SubElement(text_element, "title")
    title_element.text = (
        "Output from CDC PRIME DIBBs `message-refiner` API by request of STLT"
    )

    table_element = etree.SubElement(text_element, "table", border="1")
    tr_element = etree.SubElement(table_element, "tr")
    td_element = etree.SubElement(tr_element, "td")
    td_element.text = "Section details have been removed as requested"

    # remove all <entry> elements
    for entry in section.findall(".//hl7:entry", namespaces=namespaces):
        section.remove(entry)

    # add nullFlavor="NI" to the <section> element
    section.attrib["nullFlavor"] = "NI"
