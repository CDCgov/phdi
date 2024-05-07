import sqlite3
from typing import Union


def sanitize_inputs_to_list(value: Union[list, str, int, float]) -> list:
    """
    Small helper function that checks the type of the input.
    Our code wants items to be in a list and will transform int/float to list
    and will check if a string could potentially be a list.
    It will also remove any excess characters from the list.

    :param value: String, int, float, list to check
    :return: A list free of excess whitespace
    """
    common_delimiters = [" ", ",", "|", ";"]
    if isinstance(value, (int, float)):
        value = [str(value)]
    elif isinstance(value, str):
        for delimiter in common_delimiters:
            if delimiter in value:
                value = value.split(delimiter)
            else:
                value = [value]  # else one-item list
    # remove any whitespace, treat each item as string
    return [str(val).strip() for val in value if str(val) != " "]


def get_clinical_service_dict(
    snomed_id: Union[str, int, float], clinical_services: list = None
) -> dict:
    """
    This will take a SNOMED ID (str, int, float) and sanitize them.
    Then it runs a SQL query to takes that condition code, joins it to value
    sets, then uses the value set ids to get the clinical service type,
    clinical service code, and clinical service system from the eRSD database.

    It will then parse that information into a dictionary for use in the
    /get-value-sets API endpoint.

    There is an optional parameter to return select clinical service type(s).

    :param snomed_id: SNOMED code to check
    :param clinical_services: List of clinical service types to keep
    :return: A nested dictionary with clinical service type as the key with
    the relevant codes and code systems as objects within.
    """
    # sanitize snomeds - confirm only 1 snomed provided
    snomed_id = sanitize_inputs_to_list(snomed_id)
    if len(snomed_id) > 1:
        return print("Provide only only one SNOMED code.")

    # SQL query with placeholders
    sql_query = """
    SELECT
        vs.clinical_service_type_id AS clinical_service_type,
        cs.code AS code,
        cs.code_system AS system
    FROM
        conditions c
    JOIN
        value_sets vs ON c.value_set_id = vs.id
    JOIN
        clinical_services cs ON cs.value_set_id = vs.id
    WHERE
        c.id IN ({})
    """.format(", ".join("?" for _ in snomed_id))

    # Connect to the SQLite database, execute sql query, then close
    conn = sqlite3.connect("seed-scripts/ersd.db")
    cursor = conn.cursor()
    cursor.execute(sql_query, snomed_id)
    results = cursor.fetchall()
    conn.close()

    # Organize results by clinical service type and system
    organized_data = {}
    for clinical_service_type, code, system in results:
        if clinical_service_type not in organized_data:
            organized_data[clinical_service_type] = {}
        if system not in organized_data[clinical_service_type]:
            organized_data[clinical_service_type][system] = []
        organized_data[clinical_service_type][system].append(code)

    # Convert to the final structured format
    clinical_service_dict = {}
    for clinical_service_type, systems in organized_data.items():
        clinical_service_dict[clinical_service_type] = []
        for system, codes in systems.items():
            clinical_service_dict[clinical_service_type].append(
                {"codes": codes, "system": system}
            )

    # Optional: Remove clinical service types not in specified list if provided
    if clinical_services:
        clinical_services = sanitize_inputs_to_list(clinical_services)
        # Create a list of types to remove
        remove_list = [
            type
            for type in clinical_service_dict.keys()
            if type not in clinical_services
        ]
        # Remove the types
        for type in remove_list:
            clinical_service_dict.pop(type, None)
    return clinical_service_dict
