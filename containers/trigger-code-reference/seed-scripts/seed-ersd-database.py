import ast
import json
import os
import sqlite3
import time
from pathlib import Path
from typing import List

import docker
import requests
from docker.errors import APIError
from docker.errors import BuildError
from docker.models.containers import Container
from dotenv import load_dotenv

load_dotenv()
# eRSD constants, can be obtained at: https://ersd.aimsplatform.org/#/api-keys
ERSD_API_KEY = os.getenv("ERSD_API_KEY")
ERSD_URL = f"https://ersd.aimsplatform.org/api/ersd/v2specification?format=json&api-key={ERSD_API_KEY}"

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
        client.images.build(path=str(dockerfile_path), tag=tag)
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


def build_clinical_services_dict(data: dict) -> dict:
    """
    This is the only part of the parsed json bundle where the service type
    and version are defined for each of the value sets, so this function makes
    a dictionary that has each value_set_id as a key with its service type id
    and version.

    :param data: message-parser parsed eRSD json
    :return: a dictionary of each value_set URL with its service type and
             version.
    """
    clinical_services_dict = {}
    for value_set in data.get("value_sets"):
        clinical_service_type = value_set.get("clinical_service_type_id")
        version = value_set.get("version")
        compose_codes = value_set.get("compose_codes").split(",")
        for compose_code in compose_codes:
            value_set_id = compose_code.split("/")[-1]
            clinical_services_dict[value_set_id] = {
                "clinical_service_type": clinical_service_type,
                "version": version,
            }
    return clinical_services_dict


def check_id_uniqueness(list_of_lists: List[List[str]]) -> bool:
    """This is a helper function that confirms that the first item
    in each list of the lists of lists is unique. This is needed to
    confirm that the assumptions we have about tables with a unique primary
    key (value_sets, value_set_types, clinical_services) are all in fact
    unique (i.e., the number of unique ids matches number of rows).
    If not, then the function will exit to prevent overwriting.

    :param list_of_lists: eRSD table data to be transformed into table.
    :return: True or False.
    """
    unique_ids = {sublist[0] for sublist in list_of_lists if sublist}
    return len(unique_ids) == len(list_of_lists)


def build_value_set_type_table(data: dict) -> List[List[str]]:
    """
    Loop through parsed json bundle in order to build a small table of
    each of the (currently) 6 service types as defined by APHL with its id
    and short description of the clinical service type.

    :param data: message-parser parsed eRSD json
    :return: a list of lists of the id and type of each of the service types
             to load to a database
    """
    value_set_type_list = []
    for value_set_type in data.get("value_set_type"):
        id = value_set_type.get("id")
        type = value_set_type.get("clinical_service_type")
        value_set_type_list.append([id, type])
    if check_id_uniqueness(value_set_type_list):
        return value_set_type_list
    else:
        return print("Non-unique IDs in value_set_type")


def build_value_sets_table(data: dict, clinical_services_dict: dict) -> List[List[str]]:
    """
    Look through eRSD json to create value sets table, where the primary key
    is the value_set_id that contains the name and codes for each service.

    It also uses the clinical services dictionary that will have the clinical
    service type for each of the services as well as the value set version.

    :param data: message-parser parsed eRSD json
    :param clinical_services_dict: a dictionary of each value_set URL with its
    service type as value
    :return: list of lists of for each of the value set id, name, and code info
    """
    clinical_services = data.get("clinical_services")
    value_sets_list = []
    for service in clinical_services:
        value_set_id = service.get("value_set_id")
        value_set_name = service.get("display")
        publisher = service.get("publisher")
        service_info = clinical_services_dict.get(value_set_id)
        result = [
            value_set_id,
            service_info.get("version", ""),
            value_set_name,
            publisher,
            service_info.get("clinical_service_type"),
        ]
        value_sets_list.append(result)
    if check_id_uniqueness(value_sets_list):
        return value_sets_list
    else:
        return print("Non-unique IDs in value_sets")


def build_conditions_table(data: dict) -> List[List[str]]:
    """
    Look through eRSD json to create conditions table, where the primary key
    is a SNOMED condition code and has the name and system for each condition.

    :param data: message-parser parsed eRSD json
    :return: list of lists of for each of the condition code, name, and system
    """
    clinical_services = data.get("clinical_services")
    conditions_list = []
    for service in clinical_services:
        value_set_id = service.get("value_set_id")
        valueable_codes = ast.literal_eval(service.get("valueable_codes"))
        if isinstance(valueable_codes, dict):  # one item, need to list it
            valueable_codes = [valueable_codes]
        # valueable codes to build value_set
        for valueable_code in valueable_codes:
            code_system = valueable_code.get("coding")[0].get("system")
            code = valueable_code.get("coding")[0].get("code")
            code_name = valueable_code.get("text")
            result = [code, value_set_id, code_system, code_name]
            conditions_list.append(result)
    return conditions_list


def build_clinical_services_table(data: dict) -> List[List[str]]:
    """
    This builds the table for clinical services, which has a unique row for
    each unique value_set_id-code combination.

    :param data: message-parser parsed eRSD json
    :return: list of lists of for each unique value_set_id-code-id, name, and
    code info
    """
    clinical_services = data.get("clinical_services")
    clinical_services_list = []
    for service in clinical_services:
        value_set_id = service.get("value_set_id")
        compose_codes = ast.literal_eval(service.get("compose_codes"))
        if isinstance(compose_codes, dict):  # one item, need to list it
            compose_codes = [compose_codes]
        for compose_code in compose_codes:
            version = compose_code.get("version", "")
            system = compose_code.get("system", "")
            for concept in compose_code.get("concept"):
                code = concept.get("code", "")
                display = concept.get("display", "")
                id = f"{value_set_id}_{code}"
                result = [id, value_set_id, code, system, display, version]
                clinical_services_list.append(result)
    if check_id_uniqueness(clinical_services_list):
        return clinical_services_list
    else:
        return print("Non-unique IDs in clinical_services")


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
):
    """
    Takes the sqlite3 connection to insert data created in other data steps

    :param connection: sqlite3 connection
    :param table_name: name of the table
    :param insert_rows: list of lists of values to insert into table
    """
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
    # 1. extract and transform eRSD data
    ersd_data = load_ersd(ERSD_URL)

    # 2. use message-parser to parse eRSD data, then spin down service
    container = start_docker_service(dockerfile_path, tag, ports)
    parsed_data = parse_ersd(ports, ersd_data)
    if container:
        container.stop()
        container.remove()

    # 3. used parsed data to create needed tables as list of lists
    value_set_type_list = build_value_set_type_table(parsed_data)
    clinical_services_dict = build_clinical_services_dict(parsed_data)
    value_sets_list = build_value_sets_table(parsed_data, clinical_services_dict)
    conditions_list = build_conditions_table(parsed_data)
    clinical_services_list = build_clinical_services_table(parsed_data)

    # Create mini-dict to loop through for sqlite queries
    table_dict = {
        "value_set_type": value_set_type_list,
        "value_sets": value_sets_list,
        "conditions": conditions_list,
        "clinical_services": clinical_services_list,
    }

    with sqlite3.connect("seed-scripts/ersd.db") as conn:
        # 4. Delete existing tables in eRSD database
        for table_name in table_dict.keys():
            delete_table(conn, table_name)

        # 5. Create tables in eRSD database
        apply_migration(
            conn, "seed-scripts/migrations/V01_01__create_tables_add_indexes.sql"
        )

        # 6. Insert data into the tables
        for table_name, table_rows in table_dict.items():
            load_table(conn, table_name, table_rows)


if __name__ == "__main__":
    main()
