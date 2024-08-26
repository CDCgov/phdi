import ast
import json
import os
import sqlite3
import string
import time
from pathlib import Path
from typing import List
from typing import Tuple

import docker
import requests
from docker.errors import APIError
from docker.errors import BuildError
from docker.models.containers import Container
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()
# eRSD constants, can be obtained at: https://ersd.aimsplatform.org/#/api-keys
ERSD_API_KEY = os.getenv("ERSD_API_KEY")
ERSD_URL = f"https://ersd.aimsplatform.org/api/ersd/v2specification?format=json&api-key={ERSD_API_KEY}"
UMLS_API_KEY = os.getenv("UMLS_API_KEY")

# docker constants to start message-parser service
dockerfile_path = Path(__file__).parent.parent.parent / "message-parser"
tag = "message-parser:latest"
ports = {"8080": 8080}


def load_ersd(URL: str) -> dict:
    """
    Loads the latest v2 eRSD data from the eRSD API in a json format.
    :param URL: the eRSD API URL

    :return: eRSD FHIR bundle in JSON format
    """
    response = requests.get(URL)
    if response.status_code == 200:
        data = response.json()
    else:
        print("Failed to retrieve data:", response.status_code, response.text)
    return data


def load_vsac_api(url) -> dict:
    """
    Loads ValueSet or CodeSystem data from the VSAC FHIR API in a json format.
    :param url: API url to hit

    :return: FHIR compose data for valueset or codesystem in JSON format
    """
    response = requests.get(
        url,
        auth=HTTPBasicAuth("apikey", UMLS_API_KEY),
    )
    if response.status_code == 200:
        data = response.json()
    else:
        print("Failed to retrieve data:", response.status_code, response.text)
    return data


def start_docker_service(dockerfile_path: str, tag: str, ports: dict) -> Container:
    """
    Builds and runs a Docker container based on a Dockerfile.
    Runs the two message-parser services needed to parse eRSD data.

    :param dockerfile_path: Path to the directory containing the Dockerfile.
    :param tag: Tag to assign to the built image.
    :param ports: Port mapping for the container
    :return: returns container id in order to close once Docker work complete.
    """
    client = docker.from_env()
    container = None
    try:
        # connect and start
        client.images.build(path=str(dockerfile_path), tag=tag, platform="linux/amd64")
        container = client.containers.run(tag, ports=ports, detach=True)
        time.sleep(1.5)  # TODO: find better way to make sure service waits
    except (BuildError, APIError) as e:
        print(f"An error occurred while starting the Docker service: {str(e)}")
    return container


def load_ersd_schema(ports: dict):
    """
    Loads the ersd.json to the message-parser endpoint to use to parse eRSD
    :param ports: port for the message-parser endpoint URL
    """
    with open("seed-scripts/config/ersd.json", "r") as json_file:
        ersd_schema = json.load(json_file)
    # Create payload to upload the schema to message-parser
    url = f"http://localhost:{list(ports.values())[0]}/schemas/ersd.json"
    headers = {"Content-Type": "application/json"}
    payload = {
        "overwrite": "true",
        "parsing_schema": ersd_schema,
        "parsing_schema_name": "ersd.json",
    }
    try:
        requests.put(url=url, headers=headers, json=payload)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def parse_ersd(ports: dict, data: dict) -> dict:
    """
    Takes the eRSD bundle and posts it to the message parser. This flattens the
    eRSD bundle to a flatter json that can be parsed.

    :param ports: port for the message-parser endpoint URL
    :param data: eRSD json bundle
    :return: parsed message.
    """
    # load the ersd.json schema to message-parser first
    load_ersd_schema(ports)

    # make post-message call
    url = f"http://localhost:{list(ports.values())[0]}/parse_message"
    headers = {"Content-Type": "application/json"}
    payload = {
        "message_format": "fhir",
        "message": data,
        "parsing_schema_name": "ersd.json",
    }
    try:
        parsed_message = requests.post(url=url, headers=headers, json=payload)
        match parsed_message.status_code:
            case 200:
                return parsed_message.json().get("parsed_values")
            case 422:
                return parsed_message.json().get("message")
            case _:
                return parsed_message.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def build_valuesets_dict(data: dict) -> dict:
    """
    This is the only part of the parsed json bundle where the valueset type
    is defined for each of the valuesets, so this function makes
    a dictionary that has each valueset_id as a key with its valueset type id
    and version.

    It also looks up the version from the VSAC FHIR as a value for the dict.

    :param data: message-parser parsed eRSD json
    :return: a dictionary of each valueset URL with its valueset type and
             version.
    """
    valuesets_dict = {}
    for valueset in data.get("valuesets"):
        concept_type = valueset.get("concept_type_id")
        compose_codes = valueset.get("compose_codes").split(",")
        for compose_code in compose_codes:
            valueset_id = compose_code.split("/")[-1]
            if valueset_id not in valuesets_dict.keys():
                url = f"https://cts.nlm.nih.gov/fhir/ValueSet/{valueset_id}"
                vsac_data = load_vsac_api(url)
                version = vsac_data.get("version")
                valuesets_dict[valueset_id] = {
                    "concept_type": concept_type,
                    "version": version,
                }
    return valuesets_dict


def check_id_uniqueness(list_of_lists: List[List[str]]) -> bool:
    """This is a helper function that confirms that the first item
    in each list of the lists of lists is unique. This is needed to
    confirm that the assumptions we have about tables with a unique primary
    key (valuesets, valueset_types, concepts) are all in fact
    unique (i.e., the number of unique ids matches number of rows).
    If not, then the function will exit to prevent overwriting.

    :param list_of_lists: eRSD table data to be transformed into table.
    :return: True or False.
    """
    unique_ids = {sublist[0] for sublist in list_of_lists if sublist}
    return len(unique_ids) == len(list_of_lists)


def build_valuesets_table(
    data: dict,
    valuesets_dict: dict,
) -> Tuple[List[List[str]], List[List[str]]]:
    """
    Look through eRSD json to create valuesets table, where the primary key
    is the valueset_id that contains the name and codes for each service.

    It will create a junction table between valueset id, condition id, and log
    version of the eRSD table.

    It also outputs a dictionary of the valueset:version to use for the other
    junction table to avoid duplicative API calls.

    :param data: message-parser parsed eRSD json
    :param valuesets_dict: a dictionary of each valueset URL with its
    service type and versions as values
    :return: list of lists of for each of the valueset id, name, and code info;
             list of lists of each valueset id, condition id, source/version
             dict of the valuesets with version
    """
    concepts = data.get("concepts")
    ersd_version = data.get("valuesets")[0].get("ersd_version")
    valuesets_list = []
    junction_list = []
    for service in concepts:
        valueset_id = service.get("valueset_id")
        valueset_name = service.get("display")
        publisher = service.get("publisher")
        service_info = valuesets_dict.get(valueset_id)
        version = service_info.get("version")
        id = f"{valueset_id}_{version}"
        result = [
            id,
            valueset_id,
            version,
            valueset_name,
            publisher,
            service_info.get("concept_type"),
        ]
        valuesets_list.append(result)
        # create junction table between valueset ID and condition ID
        concept_codes = ast.literal_eval(service.get("valueable_codes"))
        if isinstance(concept_codes, dict):
            concept_codes = [concept_codes]
        for concept in concept_codes:
            code = concept.get("coding")[0].get("code")
            junction_list.append([code, id, f"eRSD_{ersd_version}"])
    if check_id_uniqueness(valuesets_list):
        return valuesets_list, junction_list
    else:
        print("Non-unique IDs in valuesets")
        return [], []


def build_conditions_table(data: dict) -> List[List[str]]:
    """
    Look through eRSD json to create conditions table, where the primary key
    is a SNOMED condition code and has the name and system for each condition.

    :param data: message-parser parsed eRSD json
    :return: list of lists for each of the condition code, name, system,
             and version
    """
    concepts = data.get("concepts")
    conditions_list = []
    conditions_dict = {}
    for service in concepts:
        valueable_codes = ast.literal_eval(service.get("valueable_codes"))
        if isinstance(valueable_codes, dict):  # one item, need to list it
            valueable_codes = [valueable_codes]
        # valueable codes to build conditions
        for valueable_code in valueable_codes:
            code_system = valueable_code.get("coding")[0].get("system")
            code = valueable_code.get("coding")[0].get("code")
            code_name = valueable_code.get("text")
            # only run code once against API then append to list of lists
            if code not in conditions_dict.keys():
                url = f"https://cts.nlm.nih.gov/fhir/CodeSystem/$lookup?system={code_system}&code={code}"
                vsac_data = load_vsac_api(url)
                version = [
                    data.get("valueString").split("/")[-1]
                    for data in vsac_data.get("parameter")
                    if data.get("name") == "version"
                ][0]
                conditions_dict[code] = version
                results = [code, code_system, code_name, version]
                conditions_list.append(results)
    if check_id_uniqueness(conditions_list):
        return conditions_list
    else:
        print("Non-unique IDs in conditions")
        return []


def build_concepts_table(
    data: dict,
    valuesets_dict: dict,
) -> Tuple[List[List[str]], List[List[str]], dict]:
    """
    This builds the table for concepts, which has a unique row for
    each unique valueset_id-concept code combination.

    It also creates a junction table between the valueset_id and concept_id.

    :param data: message-parser parsed eRSD json
    :param valuesets_dict: a dictionary of each valueset URL with its
    service type and versions as values
    :return: list of lists of for each unique valueset_id-code-id, name, and
    code info;
             list of lists for each valueset_id, concept_id
    """
    concepts = data.get("concepts")
    concepts_list = []
    junction_list = []
    for service in concepts:
        valueset_id = service.get("valueset_id")
        compose_codes = ast.literal_eval(service.get("compose_codes"))
        if isinstance(compose_codes, dict):  # one item, need to list it
            compose_codes = [compose_codes]
        for compose_code in compose_codes:
            version = compose_code.get("version", "")
            system = compose_code.get("system", "")
            for concept in compose_code.get("concept"):
                code = concept.get("code", "")
                display = concept.get("display", "")
                id = f"{valueset_id}_{code}"
                gem_formatted_code = code.translate(
                    str.maketrans("", "", string.punctuation)
                )
                result = [id, code, system, display, gem_formatted_code, version]
                concepts_list.append(result)
                # create junction table between valueset and concept
                valueset_version = valuesets_dict.get(valueset_id).get("version")
                valueset_id_full = f"{valueset_id}_{valueset_version}"
                junction_list.append([valueset_id_full, id])
    if check_id_uniqueness(concepts_list):
        return concepts_list, junction_list
    else:
        print("Non-unique IDs in concepts")
        return [], []


def build_crosswalk_table():
    """
    Reads the ICD-10-CM Generalized Equivalency Mappings file published by CMS
    to create a crosswalk table between ICD10 codes and a selected set of ICD9
    codes (the selected set are those relevant to ICD10 codes).
    """
    table_rows = []
    row_id = 1
    with open("seed-scripts/diagnosis_gems_2018/2018_I10gem.txt", "r") as gem:
        for row in gem:
            line = row.strip()
            if line != "":
                # Some formatting in the file is a tab, others are 4 spaces...
                code_components = line.split()
                code_components = [row_id] + [
                    x for x in code_components if x.strip() != ""
                ]
                table_rows.append(code_components)
                row_id += 1
    return table_rows


def apply_migration(connection: sqlite3.Connection, migration_file: str):
    """
    This function reads in sql files and executes the .sql file specified to
    the db path specified

    :param connection: sqlite3 connection
    :param migration_file: location of the .sql file to execute
    """
    with open(migration_file, "r") as file:
        sql_script = file.read()
    cursor = connection.cursor()
    try:
        cursor.executescript(sql_script)
        connection.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        connection.rollback()


def delete_table(connection: sqlite3.Connection, table_name: str):
    """
    Takes the sqlite3 connection to delete existing tables from database

    :param connection: sqlite3 connection
    :param table_name: name of the table
    """
    cursor = connection.cursor()
    try:
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        connection.rollback()


def load_table(
    connection: sqlite3.Connection,
    table_name: str,
    insert_rows: List[List[str]],
    auto_increment_id: bool = False,
):
    """
    Takes the sqlite3 connection to insert data created in other data steps

    :param connection: sqlite3 connection
    :param table_name: name of the table
    :param insert_rows: list of lists of values to insert into table
    :param auto_increment_id: boolean to determine whether table needs
            sequential row number as primary id
    """
    if auto_increment_id:
        insert_rows = [[i + 1] + row for i, row in enumerate(insert_rows)]
    cursor = connection.cursor()
    try:
        values = ", ".join("?" for _ in insert_rows[0])
        sql_query = f"INSERT into {table_name} VALUES ({values})"
        cursor.executemany(sql_query, insert_rows)
        connection.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        connection.rollback()


def main():
    """
    Runs all the functions to:
    1. Load eRSD data json from APHL API.
    2. Post eRSD data json to message-parser to get parsed data.
    3. Use parsed data to create list of lists for each table.
    4. Delete existing tables in sqlite database.
    5. Create tables and add indexes.
    6. Insert data into tables.
    """
    # 1. Load eRSD data json from APHL API.
    print("Loading eRSD data...")
    ersd_data = load_ersd(ERSD_URL)

    # 2. Post eRSD data json to message-parser to get parsed data.
    print("Instantiating the message parser...")
    container = start_docker_service(dockerfile_path, tag, ports)
    print("Parsing the eRSD...")
    parsed_data = parse_ersd(ports, ersd_data)
    if container:
        container.stop()
        container.remove()

    # 3. se parsed data to create list of lists for each table.
    print("Building valuesets and condition mappings...")
    valuesets_dict = build_valuesets_dict(parsed_data)
    valuesets_list, condition_to_valueset_list = build_valuesets_table(
        parsed_data, valuesets_dict
    )
    print("Building concepts and valueset mappings")
    conditions_list = build_conditions_table(parsed_data)
    concepts_list, valueset_to_concept_list = build_concepts_table(
        parsed_data, valuesets_dict
    )
    print("Building GEM crosswalks...")
    crosswalk_list = build_crosswalk_table()

    # Create mini-dict to loop through for sqlite queries
    table_dict = {
        "valuesets": valuesets_list,
        "conditions": conditions_list,
        "concepts": concepts_list,
        "icd_crosswalk": crosswalk_list,
        "condition_to_valueset": condition_to_valueset_list,
        "valueset_to_concept": valueset_to_concept_list,
    }

    with sqlite3.connect("seed-scripts/ersd.db") as conn:
        # 4. Delete existing tables in sqlite database.
        print("Deleting existing / old tables...")
        for table_name in table_dict.keys():
            delete_table(conn, table_name)

        # 5. Create tables and add indexes.
        print("Applying fresh DB migration...")
        apply_migration(
            conn, "seed-scripts/migrations/V02_01__create_tables_add_indexes.sql"
        )

        # 6. Insert data into tables.
        for table_name, table_rows in table_dict.items():
            print("Loading " + table_name + " table...")
            if "_to_" in table_name:  # use to add sequential row number
                load_table(conn, table_name, table_rows, True)
            else:
                load_table(conn, table_name, table_rows, False)


if __name__ == "__main__":
    main()
