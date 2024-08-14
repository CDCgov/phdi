import json
import sqlite3
from pathlib import Path
from typing import List
from typing import Union

import fhirpathpy


def convert_inputs_to_list(value: Union[list, str, int, float]) -> list:
    """
    Small helper function that checks the type of the input.
    Our code wants items to be in a list and will transform int/float to list
    and will check if a string could potentially be a list.
    It will also remove any excess characters from the list.

    :param value: string, int, float, list to check
    :return: A list free of excess whitespace
    """
    if isinstance(value, (int, float)):
        return [str(value)]
    elif isinstance(value, str):
        common_delimiters = [",", "|", ";"]
        for delimiter in common_delimiters:
            if delimiter in value:
                return [val.strip() for val in value.split(delimiter) if val.strip()]
        return [value.strip()]  # No delimiter found, return the single value
    elif isinstance(value, list):
        return [str(val).strip() for val in value if str(val).strip()]
    else:
        raise ValueError("Unsupported input type for sanitation.")


def get_clean_snomed_code(snomed_code: Union[list, str, int, float]) -> list:
    """
    This is a small helper function that takes a SNOMED code, sanitizes it,
    then checks to confirm only one SNOMED code has been provided.

    :param snomed_code: SNOMED code to check.
    :return: A one-item list of a cleaned SNOMED code.
    """
    clean_snomed_code = convert_inputs_to_list(snomed_code)
    if len(clean_snomed_code) != 1:
        return {
            "error": f"{len(clean_snomed_code)} SNOMED codes provided. "
            + "Provide only one SNOMED code."
        }
    return clean_snomed_code


def get_concepts_list(snomed_code: list) -> List[tuple]:
    """
    This will take a SNOMED code and runs a SQL query joins condition code,
    joins it to value sets, then uses the value set ids to get the
    value set type, concept codes, and concept system
    from the eRSD database grouped by value set type and system.

    :param snomed_code: SNOMED code to check
    :return: A list of tuples with value set type, a delimited-string of
    the relevant codes and code systems as objects within.
    """
    sql_query = """
    SELECT
        vs.type AS valueset_type,
        GROUP_CONCAT(cs.code, '|') AS codes,
        cs.code_system AS system
    FROM
        conditions c
    LEFT JOIN
        condition_to_valueset cv ON c.id = cv.condition_id
    LEFT JOIN
        valuesets vs ON cv.valueset_id = vs.id
    LEFT JOIN
        valueset_to_concept vc ON vs.id = vc.valueset_id
    LEFT JOIN
        concepts cs ON vc.concept_id = cs.id
    WHERE
        c.id = ?
    GROUP BY
        vs.type, cs.code_system
    """
    # Connect to the SQLite database, execute sql query, then close
    try:
        with sqlite3.connect("seed-scripts/ersd.db") as conn:
            cursor = conn.cursor()
            code = get_clean_snomed_code(snomed_code)
            cursor.execute(sql_query, code)
            concept_list = cursor.fetchall()
            # We know it's not an actual error because we didn't get kicked to
            # except, so just return the lack of results
            if not concept_list:
                return []
        return concept_list
    except sqlite3.Error as e:
        return {"error": f"An SQL error occurred: {str(e)}"}


def get_concepts_dict(
    concept_list: List[tuple],
    filter_concept_list: Union[str, list] = None,
) -> dict:
    """
    This function parses a list of tuples containing data on clinical codes
    into a dictionary for use in the /get-value-sets API endpoint.

    There is an optional parameter to return select value set type(s)
    specified as either a string or a list.

    :param concept_list: A list of tuples with value set type,
    a delimited-string of relevant codes and code systems as objects within.
    :param filter_concept_list: (Optional) List of value set types
    specified to keep. By default, all (currently) 6 value set types are
    returned; use this parameter to return only types of interest.
    :return: A nested dictionary with value set type as the key, a list
    of the relevant codes and code systems as objects within.
    """
    # Convert to the final structured format
    concept_dict = {}
    for concept_type, codes_string, system in concept_list:
        # If concept_type is not yet in the dictionary, initialize
        if concept_type not in concept_dict:
            concept_dict[concept_type] = []
        # Append a new entry with the codes and their system
        concept_dict[concept_type].append(
            {"codes": codes_string.split("|"), "system": system}
        )

    # Optional: Remove value set types not in specified list if provided
    if filter_concept_list:
        concepts = convert_inputs_to_list(filter_concept_list)
        # Create a list of types to remove
        remove_list = [type for type in concept_dict.keys() if type not in concepts]
        # Remove the types
        for type in remove_list:
            concept_dict.pop(type, None)
    return concept_dict


def _find_codes_by_resource_type(resource: dict) -> List[str]:
    """
    For a given resource, extracts the chief clinical codes within the
    resource body. The FHIRpath location of this resource depends on the
    type of resource passed to the function. A resource might have more
    than one clinical code denoting what type of information it holds, such
    as an Observation with a SNOMED code and a LOINC code both relating
    to a COVID-19 diagnosis.

    :param resource: The resource in which to locate the code.
    :return: One or more clinical codes, as a list of strings. If the given
      resource has no corresponding codes, an empty list is returned.
    """
    rtype = resource.get("resourceType")
    codings = []

    # Grab coding schemes based on resource type
    if rtype in ["Observation", "Condition", "DiagnosticReport"]:
        codings = resource.get("code", {}).get("coding", [])
    elif rtype == "Immunization":
        codings = resource.get("vaccineCode", {}).get("coding", [])

    # Then, isolate for the actual clinical codes
    codes = [x.get("code", "") for x in codings]

    # Also need to add valueCodeableConcepts to obs resources
    if rtype == "Observation":
        vccs = resource.get("valueCodeableConcept", {}).get("coding", [])
        codes += [x.get("code", "") for x in vccs]

    return [x for x in codes if x != ""]


def _stamp_resource_with_code_extension(resource: dict, code: str) -> dict:
    """
    Stamps a provided resource with an extension containing a passed-in
    SNOMED code. The stamping procedure adds an extension to the resource
    body without altering any other existing data.

    :param resource: The resource to stamp.
    :param code: The SNOMED code to insert an extension for.
    :return: The resource with new extension added.
    """
    if "extension" not in resource:
        resource["extension"] = []
    resource["extension"].append(
        {
            "url": "https://reportstream.cdc.gov/fhir/StructureDefinition/condition-code",
            "coding": [{"code": code, "system": "http://snomed.info/sct"}],
        }
    )
    return resource


def read_json_from_assets(filename: str) -> dict:
    """
    Reads a JSON file from the assets directory.

    :param filename: The name of the file to read.
    :return: A dictionary containing the contents of the file.
    """
    return json.load(open((Path(__file__).parent.parent / "assets" / filename)))


def find_conditions(bundle: dict) -> set[str]:
    """
    Extracts the SNOMED codes of reportable conditions from a FHIR bundle.

    :param bundle: A FHIR bundle
    :return: A set of SNOMED codes for reportable conditions
    """

    path_to_reportability_response_info_section = fhirpathpy.compile(
        "Bundle.entry.resource.where(resourceType='Composition').section.where(title = 'Reportability Response Information Section').entry"
    )
    trigger_entries = path_to_reportability_response_info_section(bundle)
    triggering_IDs = [x["reference"].split("/") for x in trigger_entries]
    codes = set()
    for type, id in triggering_IDs:
        result = fhirpathpy.evaluate(
            bundle,
            f"Bundle.entry.resource.ofType({type}).where(id='{id}').valueCodeableConcept.coding.where(system = 'http://snomed.info/sct').code",
        )

        if result:
            codes.add(result[0])

    return codes
