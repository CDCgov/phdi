from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Union

from lxml import etree
from rich import print

from app.utils import read_json_from_assets

# LOINC codes for eICR sections our refiner API accepts
REFINER_DETAILS = read_json_from_assets("refiner_details.json")

# extract LOINC codes from the REFINER_DETAILS dictionary
SECTION_LOINCS = list(REFINER_DETAILS["sections"].keys())


def validate_message(raw_message: str) -> tuple[bytes | None, str]:
    """
    Validates that an incoming XML message can be parsed by lxml's  etree .

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
    sections_to_include: Optional[List[str]] = None,
    clinical_services: Optional[List[str]] = None,
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
    namespaces = {"hl7": "urn:hl7-org:v3"}
    structured_body = validated_message.find(".//hl7:structuredBody", namespaces)

    # if no parameters are provided, return message with only
    # the observations that triggered the message and minimal sections
    # for everything that does not contain trigger code observations
    if not sections_to_include and not clinical_services:
        _process_section(REFINER_DETAILS, structured_body)
        return etree.tostring(validated_message, encoding="unicode")

    # we need to find the condition codes in the clinical_services list and then
    # extract the section LOINC codes
    if clinical_services:
        pass
        # # join the xpath expressions together
        # services_xpath_expression = " | ".join(clinical_services)
        # # grab all of the <entry> elements with the clinical_service codes
        # service_elements = validated_message.xpath(
        #     services_xpath_expression, namespaces=namespaces
        # )
        # # initialize a dictionary to hold the section code and the element
        # services_section_and_elements = {}
        # for element in service_elements:
        #     # the parent is the section element
        #     parent = element.getparent()
        #     # find the code element and extract the section LOINC
        #     code_element = parent.find(".//hl7:code", namespaces=namespaces)
        #     code = code_element.get("code")
        #     # as we create the dictionary, we want to make sure the section key is unique
        #     if code not in services_section_and_elements:
        #         services_section_and_elements[code] = []
        #     # append (<entry>) element to corresponding section key
        #     services_section_and_elements[code].append(element)

    # if we only have sections_to_include then we keep those section entirely while removing
    # all other section entries except for the trigger code observations
    if sections_to_include and not clinical_services:
        # filter out the sections to include from the REFINER_DETAILS dictionary
        # since this data structure controls the processing, removing them from the
        # dictionary will prevent the sections from being changed in any way
        refiner_details_filtered = {
            code: details
            for code, details in REFINER_DETAILS["sections"].items()
            if code not in sections_to_include
        }
        # create a new REFINER_DETAILS dictionary with the filtered sections
        refiner_details_filtered = {"sections": refiner_details_filtered}

        # process the remaining sections normally
        _process_section(refiner_details_filtered, structured_body)
        return etree.tostring(validated_message, encoding="unicode")

    # if we only have clinical_services then we use the unique sections from the
    # services_section_and_elements dictionary to include entries to refined sections
    # and minimal sections.
    # TODO: then we check for overlap with trigger_code_elements
    # if the trigger_code_elements elements are present in the refined sections, then
    # we do not need to include them. if the refined output does not include the trigger_code_elements
    # then we need to append them to the refined section(s) or the minimal section(s) they belong to
    if clinical_services and not sections_to_include:
        # elements = []
        # for section_code, entries in services_section_and_elements.items():
        #     minimal_section = __create_minimal_section(section_code, empty_section=False)
        #     for entry in entries:
        #         minimal_section.append(entry)
        #     elements.append(minimal_section)
        #
        # minimal_sections = __create_minimal_sections(
        #     sections_with_conditions=services_section_and_elements.keys(),
        #     empty_section=True,
        # )
        #
        # # check for overlap with trigger code elements and add them if not include them
        # for section_code, trigger_elements in trigger_code_elements.items():
        #     if section_code not in services_section_and_elements:
        #         minimal_sections.extend(trigger_elements)
        #
        # return _add_root_element(header, elements + minimal_sections)
        return etree.tostring(validated_message, encoding="unicode")

    # if we have both sections_to_include and clinical_services then we need to
    # prioritize the clinical_services using the sections_to_include as a locus;
    # TODO: if there is overlap with trigger_code_elements, then we do not need to include them.
    # if there is no overlap, we need to append to either the refined section(s) or the
    # minimal section(s) they belong to
    if sections_to_include and clinical_services:
        # check if there is match between sections_to_include and conditions  we want to include
        # if there is a match, these are the _only_ sections we want to include
        # matching_sections = set(sections_to_include) & set(
        #     services_section_and_elements.keys()
        # )
        # # if there is no match, we will respond with empty; minimal sections
        # if not matching_sections:
        #     minimal_sections = __create_minimal_sections()
        #     return _add_root_element(header, minimal_sections)
        #
        # elements = []
        # for section_code in matching_sections:
        #     minimal_section = __create_minimal_section(section_code, empty_section=False)
        #     for entry in services_section_and_elements[section_code]:
        #         minimal_section.append(entry)
        #     elements.append(minimal_section)
        #
        # minimal_sections = __create_minimal_sections(
        #     sections_with_conditions=matching_sections,
        #     empty_section=True,
        # )
        #
        # # check for overlap with trigger code elements and add them if not included
        # for section_code, trigger_elements in trigger_code_elements.items():
        #     if section_code not in matching_sections:
        #         minimal_sections.extend(trigger_elements)
        #
        # return _add_root_element(header, elements + minimal_sections)
        return etree.tostring(validated_message, encoding="unicode")


def _get_section_details(section_code: str, config: dict) -> dict:
    """
    Retrieves the details of a section from the refiner configuration.

    :param section_code: The LOINC code of the section.
    :param config: The refiner configuration dictionary.
    :return: A dictionary containing the details of the section.
    """
    return config["sections"].get(section_code, {})


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


def _get_trigger_code_observation(
    section_entries: Union[List[etree.Element], Callable[..., List[etree.Element]]],
    template_id: str,
    namespaces: dict = {"hl7": "urn:hl7-org:v3"},
    *args,
    **kwargs,
) -> List[etree.Element]:
    """
    Gets the trigger code observation from a list of entries in a section of an eICR.

    :param section_entries: Either a list of <entry> elements or a function that returns such a list.
    :param template_id: The root value of the templateId attribute (OID) that identifies trigger code data.
    :param namespaces: The namespaces to use when searching for elements and defaults to 'hl7'.
    :param args: Additional arguments to pass to the callable if `section_entries` is a callable.
    :param kwargs: Additional keyword arguments to pass to the callable if `section_entries` is a callable.
    :return: A list of elements containing trigger code data.
    """
    if callable(section_entries):
        section_entries = section_entries(*args, **kwargs)

    trigger_code_elements = []
    xpath_query = f'.//hl7:observation[hl7:templateId[@root="{template_id}"]]'

    for entry in section_entries:
        trigger_code_element = entry.xpath(xpath_query, namespaces=namespaces)
        if trigger_code_element:
            trigger_code_elements.extend(trigger_code_element)

    return trigger_code_elements


def _is_template_present(
    section_entries: Union[List[etree.Element], Callable[..., List[etree.Element]]],
    template_id: str,
    namespaces: dict = {"hl7": "urn:hl7-org:v3"},
    *args,
    **kwargs,
) -> bool:
    """
    Checks if a specific templateId is present in the entries of a section.

    :param section_entries: Either a list of <entry> elements or a function that returns such a list.
    :param template_id: The root value of the templateId attribute (OID) to check for.
    :param namespaces: The namespaces to use when searching for elements and defaults to 'hl7'.
    :param args: Additional arguments to pass to the callable if `section_entries` is a callable.
    :param kwargs: Additional keyword arguments to pass to the callable if `section_entries` is a callable.
    :return: True if the templateId is present, False otherwise.
    """
    if callable(section_entries):
        section_entries = section_entries(*args, **kwargs)

    xpath_query = f'.//hl7:templateId[@root="{template_id}"]'
    for entry in section_entries:
        if entry.xpath(xpath_query, namespaces=namespaces):
            return True
    return False


def _find_path_to_entry(observation: etree.Element) -> List[etree.Element]:
    """
    Finds the path from a trigger code observation back to the <entry> element.

    :param observation: The trigger code observation element.
    :return: A list of elements from the observation back to the entry.
    """
    path = []
    current_element = observation
    while current_element.tag != "{urn:hl7-org:v3}entry":
        path.append(current_element)
        current_element = current_element.getparent()
    # add the <entry> element
    path.append(current_element)
    # reverse the path to start from <entry> -> <observation>
    return path[::-1]


def _analyze_structure(path: List[etree.Element]) -> List[Dict[str, object]]:
    """
    Analyzes the structure and sibling counts for each element in the path.

    :param path: A list of elements from <entry> to the observation.
    :return: A list of dictionaries containing the element and its sibling count.
    """
    structure_info = []
    for element in path:
        parent = element.getparent()
        if parent is not None:
            siblings = parent.findall(element.tag)
            sibling_count = len(siblings)
            structure_info.append({"element": element, "sibling_count": sibling_count})
    return structure_info


def _prune_unwanted_siblings(
    structure_info: List[Dict[str, object]], desired_element: etree.Element
):
    """
    Prunes unwanted siblings based on the desired element.

    :param structure_info: A list of dictionaries containing the element and its sibling count.
    :param desired_element: The desired element to keep.
    """
    for info in structure_info:
        element = info["element"]
        parent = element.getparent()
        if parent is not None:
            siblings = parent.findall(element.tag)
            for sibling in siblings:
                # only remove siblings that are not the desired element and not part of the collected structure info
                if sibling is not desired_element and sibling not in [
                    e["element"] for e in structure_info
                ]:
                    parent.remove(sibling)


def _retain_only_trigger_code_obs(
    section: Union[etree.Element, Callable[..., etree.Element]],
    template_id: str,
    section_entries: Callable[..., List[etree.Element]] = _get_entries_for_section,
    trigger_code_observation: Callable[
        ..., List[etree.Element]
    ] = _get_trigger_code_observation,
    *args,
    **kwargs,
) -> None:
    """
    Retain only trigger code related observations.

    :param section: The section element containing the observations or a function returning the section element.
    :param template_id: The template ID to identify the manual initiation problem observation.
    :param section_entries: A function to retrieve entries for the section.
    :param trigger_code_observation: A function to retrieve trigger code observation(s).
    :param args: Additional arguments to pass to the callable functions if needed.
    :param kwargs: Additional keyword arguments to pass to the callable functions if needed.
    """
    if callable(section):
        section = section(*args, **kwargs)

    if callable(section_entries):
        section_entries = section_entries(section, *args, **kwargs)

    section_trigger_code = trigger_code_observation(
        section_entries, template_id, *args, **kwargs
    )

    elements_to_retain: Set[etree.Element] = set()
    all_structure_info = []
    # collect structure info for all observations in the event that two trigger code
    # observations are present
    for observation in section_trigger_code:
        # find the path from <observation> -> <entry>
        entry_path = _find_path_to_entry(observation)
        # analyze how nested (or not) the path from <entry> -> <observation> is
        structure_info = _analyze_structure(entry_path)
        # return a data structure with the element and its sibling counts
        all_structure_info.append((structure_info, observation))

        # add all elements in the path to the set of elements to retain
        for info in structure_info:
            elements_to_retain.add(info["element"])

    # prune after collecting all section entry structure info (if multiple trigger code
    # observations are present)
    for structure_info, observation in all_structure_info:
        for info in structure_info:
            element = info["element"]
            parent = element.getparent()
            if parent is not None:
                siblings = parent.findall(element.tag)
                for sibling in siblings:
                    if sibling not in elements_to_retain:
                        parent.remove(sibling)


def _create_text_element(message: str, template_id: str = None) -> etree.Element:
    """
    Creates a <text> element with the provided message and optional template ID.

    :param message: The message to include in the <text> element.
    :param template_id: Optional template ID to include in the <text> element.
    :return: The created <text> element.
    """
    text_element = etree.Element("{urn:hl7-org:v3}text")
    table_element = etree.SubElement(text_element, "table")
    tr_element = etree.SubElement(table_element, "tr")

    td1 = etree.SubElement(tr_element, "td")
    td1.text = message

    td2 = etree.SubElement(tr_element, "td")
    td2.text = "CDC PRIME DIBBs `message-refiner` API by STLT"

    if template_id:
        td3 = etree.SubElement(tr_element, "td")
        td3.text = f"Template ID: {template_id}"

    return text_element


def _update_text_element(
    section: etree.Element,
    message: str,
    trigger_code: bool = False,
    template_id: str = None,
) -> None:
    """
    Updates the <text> element of a section to include information based on the provided message and trigger code.

    :param section: The section element containing the <text> element to update.
    :param message: The message to include in the <text> element.
    :param trigger_code: Boolean indicating whether to include the template ID.
    :param template_id: The template ID to include if trigger_code is True.
    """
    text_element = etree.Element("{urn:hl7-org:v3}text")
    table_element = etree.SubElement(text_element, "table")
    tr_element = etree.SubElement(table_element, "tr")

    td1 = etree.SubElement(tr_element, "td")
    td1.text = f"{message} via"

    td2 = etree.SubElement(tr_element, "td")
    td2.text = "CDC PRIME DIBBs `message-refiner` API by STLT"

    if trigger_code:
        td3 = etree.SubElement(tr_element, "td")
        td3.text = f"Template ID: {template_id}"

    existing_text_element = section.find(
        ".//hl7:text", namespaces={"hl7": "urn:hl7-org:v3"}
    )
    if existing_text_element is not None:
        section.replace(existing_text_element, text_element)
    else:
        section.insert(0, text_element)


def _create_minimal_section(section: etree.Element) -> None:
    """
    Creates a minimal section by removing all elements after the <text> element
    and adds nullFlavor="NI" to the <section> element.

    :param section: The section element to update.
    """
    namespaces = {"hl7": "urn:hl7-org:v3"}
    text_element = section.find(".//hl7:text", namespaces=namespaces)

    if text_element is None:
        text_element = etree.Element("{urn:hl7-org:v3}text")
        section.insert(0, text_element)

    following_siblings = list(section.iterchildren())[section.index(text_element) + 1 :]
    for sibling in following_siblings:
        section.remove(sibling)

    section.attrib["nullFlavor"] = "NI"


def _process_trigger_codes(
    section: etree.Element, template_id_root: str, updated_text: str
) -> None:
    """
    Processes a section by retaining only trigger code observations.

    :param section: The section element to process.
    :param template_id_root: The root value of the templateId attribute (OID).
    :param updated_text: The updated text to include in the <text> element.
    """
    _retain_only_trigger_code_obs(section=section, template_id=template_id_root)
    _update_text_element(section, updated_text, True, template_id=template_id_root)


def _process_section(trigger_data: dict, structured_body: etree.Element) -> None:
    """
    Iterates through the sections of the <structuredBody> and refines each section.

    :param trigger_data: The trigger data containing section codes and template IDs.
    :param structured_body: The structuredBody element to search within.
    """
    for section_code, section_details in trigger_data["sections"].items():
        required = section_details["required"]
        display_name = section_details["display_name"]
        minimal_fields = section_details["minimal_fields"]
        trigger_codes = section_details.get("trigger_codes", {})

        section = _get_section_by_code(structured_body, section_code)

        if section is not None:
            print(
                f"[blue]Processing section:[/blue] [bold]{display_name}[/bold] [blue]with LOINC code:[/blue] [bold]{section_code}[/bold]"
            )

            if required:
                trigger_found = False
                if trigger_codes:
                    for trigger_name, trigger_details in trigger_codes.items():
                        template_id_root = trigger_details["template_id_root"]
                        updated_text = trigger_details["updated_text"]
                        if _is_template_present(
                            section_entries=_get_entries_for_section,
                            section=section,
                            template_id=template_id_root,
                        ):
                            print(
                                f"[blue]Template found:[/blue] [bold]{template_id_root}[/bold] [blue]for section [/blue] [bold]{section_code}[/bold]"
                            )
                            print(
                                f"[yellow]Before pruning:[/yellow] [bold]{len(_get_entries_for_section(section))}[/bold] [yellow]entries.[/yellow]"
                            )
                            _process_trigger_codes(
                                section, template_id_root, updated_text
                            )
                            print(
                                f"[green]After pruning:[/green] [bold]{len(_get_entries_for_section(section))}[/bold] [green]entries.[/green]"
                            )
                            trigger_found = True
                        else:
                            print(
                                f"[red]Template {template_id_root} not found for section {section_code}.[/red]"
                            )

                    if not trigger_found:
                        print(
                            f"[red]Template not found for section {section_code}, Creating Minimal Entry.[/red]"
                        )
                        _create_minimal_section(section)
                        _update_text_element(section, minimal_fields["updated_text"])
                else:
                    _create_minimal_section(section)
                    _update_text_element(section, minimal_fields["updated_text"])
            else:
                print(
                    f"[red]Removing section: {display_name} with LOINC code: {section_code} (not required)[/red]"
                )
                structured_body.remove(section)
        else:
            if not required:
                print(
                    f"[red]No {display_name} section found for code: {section_code} (not required)[/red]"
                )
            else:
                print(f"[red]No section found for code: {section_code}[/red]")
