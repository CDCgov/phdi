import pathlib

import pytest
from app.refine import _analyze_structure
from app.refine import _are_elements_present
from app.refine import _create_minimal_section
from app.refine import _create_or_update_text_element
from app.refine import _extract_observation_data
from app.refine import _find_path_to_entry
from app.refine import _generate_combined_xpath
from app.refine import _get_entries_for_section
from app.refine import _get_observations
from app.refine import _get_section_by_code
from app.refine import _process_section
from app.refine import _prune_unwanted_siblings
from app.refine import _update_text_element
from app.refine import refine
from app.refine import validate_message
from app.refine import validate_sections_to_include
from lxml import etree

TRIGGER_CODE_TEMPLATE_IDS = [
    "2.16.840.1.113883.10.20.15.2.3.5",
    "2.16.840.1.113883.10.20.15.2.3.3",
    "2.16.840.1.113883.10.20.15.2.3.4",
    "2.16.840.1.113883.10.20.15.2.3.2",
]

NAMESPACES = {"hl7": "urn:hl7-org:v3"}


def parse_file_from_test_assets(filename: str) -> etree.ElementTree:
    """
    Parses a file from the assets directory into an ElementTree.

    :param filename: The name of the file to read.
    :return: An ElementTree containing the contents of the file.
    """
    with open(
        (pathlib.Path(__file__).parent.parent / "tests" / "assets" / filename), "r"
    ) as file:
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(file, parser)
        return tree


def read_file_from_test_assets(filename: str) -> str:
    """
    Reads a file from the assets directory.

    :param filename: The name of the file to read.
    :return: A string containing the contents of the file.
    """
    with open(
        (pathlib.Path(__file__).parent.parent / "tests" / "assets" / filename),
        "r",
    ) as file:
        return file.read()


def normalize_xml(xml_string):
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.XML(xml_string, parser)
    return etree.tostring(tree, pretty_print=True).decode()


test_file = read_file_from_test_assets("CDA_eICR.xml")
test_message = parse_file_from_test_assets("message_refiner_test_eicr.xml")
test_clinical_document = test_message.getroot()
test_structured_body = test_clinical_document.find(
    ".//{urn:hl7-org:v3}structuredBody", NAMESPACES
)
encounters_section = _get_section_by_code(test_structured_body, "46240-8")
results_section = _get_section_by_code(test_structured_body, "30954-2")
social_history_section = _get_section_by_code(test_structured_body, "29762-2")
chlymidia_xpath = './/hl7:observation[hl7:templateId[@root="2.16.840.1.113883.10.20.15.2.3.2"]] | .//hl7:observation[hl7:code[@code="53926-2"]]'
chlamydia_observations = _get_observations(
    section=results_section, combined_xpath=chlymidia_xpath
)
chlamydia_observation = chlamydia_observations[2]


@pytest.mark.parametrize(
    "test_data, expected_result",
    [
        # Test case: single sections_to_include
        (
            "29762-2",
            (["29762-2"], ""),
        ),
        # Test case: multiple sections_to_include
        (
            "10164-2,29299-5",
            (["10164-2", "29299-5"], ""),
        ),
        # Test case: no sections_to_include
        (
            None,
            (None, ""),
        ),
        # Test case: invalid sections_to_include
        (
            "blah blah blah",
            ([], "blah blah blah is invalid. Please provide a valid section."),
        ),
    ],
)
def test_validate_sections_to_include(test_data, expected_result):
    # Test cases: single and multiple sections_to_include
    if test_data != "blah blah blah" and test_data is not None:
        actual_response = validate_sections_to_include(test_data)
        assert actual_response == expected_result
        assert isinstance(actual_response[0], list)
    # Test case: no sections_to_include
    elif test_data is None:
        actual_response = validate_sections_to_include(test_data)
        assert actual_response == expected_result
        assert actual_response[0] is None
    # Test case: invalid sections_to_include
    else:
        actual_response = validate_sections_to_include(test_data)
        assert actual_response == expected_result
        assert actual_response[1] != ""


def test_validate_message():
    # Test case: valid XML
    raw_message = test_file
    actual_response, error_message = validate_message(raw_message)
    actual_flattened = [i.tag for i in actual_response.iter()]
    expected_flattened = [i.tag for i in etree.fromstring(raw_message).iter()]
    assert actual_flattened == expected_flattened
    assert error_message == ""

    # Test case: invalid XML
    raw_message = "this is not a valid XML"
    actual_response, error_message = validate_message(raw_message)
    assert actual_response is None
    assert "XMLSyntaxError" in error_message


def test_generate_combined_xpath():
    template_ids = ["2.16.840.1.113883.10.20.15.2.3.2"]
    clinical_services_dict = {
        "loinc": ["95423-0", "96764-6"],
        "snomed": ["138389411000119105", "1119302008"],
    }

    expected_xpath = (
        './/hl7:observation[hl7:templateId[@root="2.16.840.1.113883.10.20.15.2.3.2"]] | '
        './/hl7:observation[hl7:code[@code="95423-0"]] | '
        './/hl7:observation[hl7:code[@code="96764-6"]] | '
        './/hl7:observation[hl7:code[@code="138389411000119105"]] | '
        './/hl7:observation[hl7:code[@code="1119302008"]]'
    )

    output = _generate_combined_xpath(template_ids, clinical_services_dict)
    assert output == expected_xpath


@pytest.mark.parametrize(
    "test_section_code, expected_section_code",
    [
        ("46240-8", "46240-8"),
        ("30954-2", "30954-2"),
        ("29762-2", "29762-2"),
        ("12345", None),
    ],
)
def test_get_section_by_code(
    test_section_code,
    expected_section_code,
):
    test_section = _get_section_by_code(test_structured_body, test_section_code)
    if test_section is not None:
        assert test_section is not None
        assert test_section.tag.endswith("section")
        assert (
            test_section.xpath("./hl7:code/@code", namespaces=NAMESPACES)[0]
            == expected_section_code
        )
    else:
        assert test_section is None


@pytest.mark.parametrize(
    "section, expected_length",
    [(encounters_section, 1), (results_section, 7), (social_history_section, 9)],
)
def test_get_entries_for_section(section, expected_length):
    entries = _get_entries_for_section(section, NAMESPACES)
    assert len(entries) == expected_length

    # check that all returned elements are <entry> elements
    for entry in entries:
        assert entry.tag.endswith("entry")


@pytest.mark.parametrize(
    "section, combined_xpath, expected_length",
    [
        (
            results_section,
            _generate_combined_xpath(
                template_ids=TRIGGER_CODE_TEMPLATE_IDS, clinical_services_dict={}
            ),
            3,
        ),
        (results_section, chlymidia_xpath, 4),
    ],
)
def test_get_observations(section, combined_xpath, expected_length):
    observations = _get_observations(section, combined_xpath, NAMESPACES)
    assert len(observations) == expected_length

    # check that all returned elements are <observation> elements
    for obs in observations:
        assert obs.tag.endswith("observation")


@pytest.mark.parametrize(
    "section, search_type, search_values, expected_result",
    [
        (
            results_section,
            "templateId",
            ["2.16.840.1.113883.10.20.15.2.3.2", "non-existent-templateId"],
            True,
        ),
        (results_section, "templateId", ["non-existent-templateId"], False),
        (results_section, "code", ["53926-2", "non-existent-code"], True),
        (results_section, "code", ["non-existent-code"], False),
    ],
)
def test_are_elements_present(section, search_type, search_values, expected_result):
    assert (
        _are_elements_present(section, search_type, search_values, NAMESPACES)
        == expected_result
    )


@pytest.mark.parametrize(
    "observation, expected_path",
    [
        (
            chlamydia_observation,
            [
                chlamydia_observations[2]
                .getparent()
                .getparent()
                .getparent(),  # <entry>
                chlamydia_observations[2].getparent().getparent(),  # <organizer>
                chlamydia_observations[2].getparent(),  # <component>
                chlamydia_observations[2],  # <observation>
            ],
        )
    ],
)
def test_find_path_to_entry(observation, expected_path):
    path = _find_path_to_entry(observation)
    assert path == expected_path
    assert len(path) == len(expected_path)


@pytest.mark.parametrize(
    "path, expected_structure_info",
    [
        (
            [
                chlamydia_observations[2]
                .getparent()
                .getparent()
                .getparent(),  # <entry>
                chlamydia_observations[2].getparent().getparent(),  # <organizer>
                chlamydia_observations[2].getparent(),  # <component>
                chlamydia_observations[2],  # <observation>
            ],
            [
                {
                    "element": chlamydia_observations[2]
                    .getparent()
                    .getparent()
                    .getparent(),
                    "sibling_count": 7,
                },
                {
                    "element": chlamydia_observations[2].getparent().getparent(),
                    "sibling_count": 1,
                },
                {"element": chlamydia_observations[2].getparent(), "sibling_count": 1},
                {"element": chlamydia_observations[2], "sibling_count": 1},
            ],
        )
    ],
)
def test_analyze_structure(path, expected_structure_info):
    structure_info = _analyze_structure(path)
    assert structure_info == expected_structure_info


@pytest.mark.parametrize(
    "xml_content, xpath, expected_entry_count",
    [
        (
            """
        <section xmlns="urn:hl7-org:v3">
          <entry>
            <organizer>
              <component>
                <observation>
                  <templateId root="2.16.840.1.113883.10.20.22.4.2"/>
                  <code code="12345-6"/>
                </observation>
              </component>
            </organizer>
          </entry>
          <entry>
            <organizer>
              <component>
                <observation>
                  <templateId root="2.16.840.1.113883.10.20.22.4.2"/>
                  <code code="67890-1"/>
                </observation>
              </component>
            </organizer>
          </entry>
          <entry>
            <organizer>
              <component>
                <observation>
                  <templateId root="2.16.840.1.113883.10.20.22.4.2"/>
                  <code code="11111-2"/>
                </observation>
              </component>
            </organizer>
          </entry>
        </section>
        """,
            './/hl7:observation[hl7:code/@code="12345-6" or hl7:code/@code="67890-1"]',
            2,
        ),
        # future test cases here if needed
    ],
)
def test_prune_unwanted_siblings(xml_content, xpath, expected_entry_count):
    element = etree.fromstring(xml_content)

    # find matching observations
    matching_observations = _get_observations(element, xpath, NAMESPACES)

    # collect paths
    paths = [_find_path_to_entry(obs) for obs in matching_observations]

    # prune unwanted siblings
    _prune_unwanted_siblings(paths, matching_observations)

    # check the number of remaining <entry> elements
    remaining_entries = _get_entries_for_section(element)
    assert len(remaining_entries) == expected_entry_count


@pytest.mark.parametrize(
    "observation, expected_data",
    [
        (
            chlamydia_observations[0],
            {
                "display_text": "Bordetella pertussis Ab [Units/volume] in Serum",
                "code": "11585-7",
                "code_system": "LOINC",
                "is_trigger_code": True,
            },
        ),
        (
            chlamydia_observations[1],
            {
                "display_text": "Bordetella pertussis [Presence] in Throat by Organism specific culture",
                "code": "548-8",
                "code_system": "LOINC",
                "is_trigger_code": True,
            },
        ),
        (
            chlamydia_observations[2],
            {
                "display_text": "Chlamydia trachomatis rRNA [Presence] in Vaginal fluid by NAA with probe detection",
                "code": "53926-2",
                "code_system": "loinc.org",
                "is_trigger_code": False,
            },
        ),
        (
            chlamydia_observations[3],
            {
                "display_text": "SARS-like Coronavirus N gene [Presence] in Unspecified specimen by NAA with probe detection",
                "code": "94310-0",
                "code_system": "LOINC",
                "is_trigger_code": True,
            },
        ),
    ],
)
def test_extract_observation_data(observation, expected_data):
    data = _extract_observation_data(observation)
    assert data == expected_data


@pytest.mark.parametrize(
    "observations, expected_text_xml",
    [
        (
            chlamydia_observations,
            b'<ns0:text xmlns:ns0="urn:hl7-org:v3"><title>Output from CDC PRIME DIBBs `message-refiner` API by request of STLT</title><table border="1"><tr><th>Display Text</th><th>Code</th><th>Code System</th><th>Trigger Code Observation</th></tr><tr><td>Bordetella pertussis Ab [Units/volume] in Serum</td><td>11585-7</td><td>LOINC</td><td>TRUE</td></tr><tr><td>Bordetella pertussis [Presence] in Throat by Organism specific culture</td><td>548-8</td><td>LOINC</td><td>TRUE</td></tr><tr><td>Chlamydia trachomatis rRNA [Presence] in Vaginal fluid by NAA with probe detection</td><td>53926-2</td><td>loinc.org</td><td>FALSE</td></tr><tr><td>SARS-like Coronavirus N gene [Presence] in Unspecified specimen by NAA with probe detection</td><td>94310-0</td><td>LOINC</td><td>TRUE</td></tr></table></ns0:text>',
        )
    ],
)
def test_create_or_update_text_element(observations, expected_text_xml):
    text_element = _create_or_update_text_element(observations)
    actual_string = etree.tostring(text_element)
    assert actual_string == expected_text_xml


@pytest.mark.parametrize(
    "section_xml, observations_xml, expected_text_xml",
    [
        (
            """<section xmlns="urn:hl7-org:v3"/>""",
            [
                """<observation xmlns="urn:hl7-org:v3">
                <templateId root="2.16.840.1.113883.10.20.22.4.2"/>
                <templateId root="2.16.840.1.113883.10.20.15.2.3.2"/>
                <code code="12345-6" displayName="Test Display 1" codeSystemName="LOINC"/>
            </observation>""",
                """<observation xmlns="urn:hl7-org:v3">
                <templateId root="2.16.840.1.113883.10.20.22.4.2"/>
                <code code="67890-1" displayName="Test Display 2" codeSystemName="LOINC"/>
            </observation>""",
            ],
            b"""<text xmlns="urn:hl7-org:v3">
            <title>Output from CDC PRIME DIBBs `message-refiner` API by request of STLT</title>
            <table border="1">
              <tr>
                <th>Display Text</th>
                <th>Code</th>
                <th>Code System</th>
                <th>Trigger Code Observation</th>
              </tr>
              <tr>
                <td>Test Display 1</td>
                <td>12345-6</td>
                <td>LOINC</td>
                <td>TRUE</td>
              </tr>
              <tr>
                <td>Test Display 2</td>
                <td>67890-1</td>
                <td>LOINC</td>
                <td>FALSE</td>
              </tr>
            </table>
        </text>""",
        )
    ],
)
def test_update_text_element(section_xml, observations_xml, expected_text_xml):
    section = etree.fromstring(section_xml)
    observations = [etree.fromstring(obs_xml) for obs_xml in observations_xml]

    _update_text_element(section, observations)

    text_element = section.find(".//{urn:hl7-org:v3}text")
    actual_string = etree.tostring(text_element, pretty_print=True).decode()
    expected_string = etree.tostring(
        etree.fromstring(expected_text_xml), pretty_print=True
    ).decode()

    assert normalize_xml(actual_string) == normalize_xml(expected_string)


@pytest.mark.parametrize(
    "section_xml, expected_section_xml",
    [
        (
            """<section xmlns="urn:hl7-org:v3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xmlns:voc="http://www.lantanagroup.com/voc" xmlns:cda="urn:hl7-org:v3" xmlns:sdtc="urn:hl7-org:sdtc">
            <templateId root="2.16.840.1.113883.10.20.22.2.3"/>
            <templateId root="2.16.840.1.113883.10.20.22.2.3" extension="2015-08-01"/>
            <templateId root="2.16.840.1.113883.10.20.22.2.3.1"/>
            <templateId root="2.16.840.1.113883.10.20.22.2.3.1" extension="2015-08-01"/>
            <code code="30954-2" codeSystem="2.16.840.1.113883.6.1" codeSystemName="LOINC" displayName="Relevant diagnostic tests and/or laboratory data"/>
            <title>Results</title>
            <text>
                <table></table>
            </text>
            <entry></entry>
            <entry></entry>
        </section>""",
            b"""<section xmlns="urn:hl7-org:v3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xmlns:voc="http://www.lantanagroup.com/voc" xmlns:cda="urn:hl7-org:v3" xmlns:sdtc="urn:hl7-org:sdtc" nullFlavor="NI">
            <templateId root="2.16.840.1.113883.10.20.22.2.3"/>
            <templateId root="2.16.840.1.113883.10.20.22.2.3" extension="2015-08-01"/>
            <templateId root="2.16.840.1.113883.10.20.22.2.3.1"/>
            <templateId root="2.16.840.1.113883.10.20.22.2.3.1" extension="2015-08-01"/>
            <code code="30954-2" codeSystem="2.16.840.1.113883.6.1" codeSystemName="LOINC" displayName="Relevant diagnostic tests and/or laboratory data"/>
            <title>Results</title>
            <text>
                <title>Output from CDC PRIME DIBBs `message-refiner` API by request of STLT</title>
                <table border="1">
                  <tr>
                    <td>Section details have been removed as requested</td>
                  </tr>
                </table>
            </text>
        </section>""",
        )
    ],
)
def test_create_minimal_section(section_xml, expected_section_xml):
    section = etree.fromstring(section_xml)

    _create_minimal_section(section)

    actual_string = etree.tostring(section, pretty_print=True).decode()
    expected_string = etree.tostring(
        etree.fromstring(expected_section_xml), pretty_print=True
    ).decode()

    assert normalize_xml(actual_string) == normalize_xml(expected_string)


@pytest.mark.parametrize(
    "combined_xpaths, clinical_services_codes, expected_in_results",
    [
        # test case 1: Process section with a match (Chlamydia code)
        (
            _generate_combined_xpath(
                template_ids=TRIGGER_CODE_TEMPLATE_IDS,
                clinical_services_dict={"loinc": ["53926-2"]},
            ),
            ["53926-2"],
            True,
        ),
        # test case 2: Process section without a match (Zika code)
        (
            _generate_combined_xpath(
                template_ids=TRIGGER_CODE_TEMPLATE_IDS,
                clinical_services_dict={"loinc": ["85622-9"]},
            ),
            ["85622-9"],
            False,
        ),
    ],
)
def test_process_section(combined_xpaths, clinical_services_codes, expected_in_results):
    _process_section(
        section=results_section,
        combined_xpaths=combined_xpaths,
        namespaces=NAMESPACES,
        template_ids=TRIGGER_CODE_TEMPLATE_IDS,
        clinical_services_codes=clinical_services_codes,
    )
    if expected_in_results:
        assert _are_elements_present(results_section, "code", ["53926-2"], NAMESPACES)
    else:
        assert not _are_elements_present(
            results_section, "code", ["53926-2"], NAMESPACES
        )


@pytest.mark.parametrize(
    "sections_to_include, conditions_to_include, expected_in_results",
    [
        # test case 1: refine with no parameters
        (None, None, False),
        # test case 1: refine with clinical services
        (None, {"loinc": ["53926-2"]}, True),
        # test case 2: refine with wrong sections_to_include for code
        (["29762-2"], {"loinc": ["53926-2"]}, False),
        # test case 3: refine with correct sections_to_include for code
        (["30954-2"], {"loinc": ["53926-2"]}, True),
    ],
)
def test_refine(sections_to_include, conditions_to_include, expected_in_results):
    fresh_test_data = parse_file_from_test_assets("message_refiner_test_eicr.xml")
    fresh_clinical_document = fresh_test_data.getroot()

    sections = None
    if sections_to_include:
        sections = sections_to_include

    clinical_services = None
    if conditions_to_include:
        clinical_services = conditions_to_include

    test_refined_output = refine(
        validated_message=fresh_clinical_document,
        sections_to_include=sections,
        clinical_services=clinical_services,
    )
    test_refined_document = etree.fromstring(test_refined_output)
    test_refined_structured_body = test_refined_document.find(
        ".//{urn:hl7-org:v3}structuredBody", NAMESPACES
    )
    test_refined_results_section = _get_section_by_code(
        test_refined_structured_body, "30954-2"
    )
    if expected_in_results:
        assert _are_elements_present(
            test_refined_results_section, "code", ["53926-2"], NAMESPACES
        )
    else:
        assert not _are_elements_present(
            test_refined_results_section, "code", ["53926-2"], NAMESPACES
        )
