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

# python constants to start message-parser service
dockerfile_path = Path(__file__).parent.parent.parent / "message-parser"
tag = "message-parser:latest"
ports = {"8080": 8080}

# SQL queries to initialize each table we need
value_set_type_table = """CREATE TABLE IF NOT EXISTS value_set_type (
                          id TEXT PRIMARY KEY,
                          clinical_service_type TEXT
                       )
                       """

value_sets_table = """CREATE TABLE IF NOT EXISTS value_sets (
                      id TEXT PRIMARY KEY,
                      version TEXT,
                      value_set_name TEXT,
                      author TEXT,
                      clinical_service_type_id
                      )
                      """

conditions_table = """CREATE TABLE IF NOT EXISTS conditions (
                      id TEXT,
                      value_set_id TEXT,
                      system TEXT,
                      name TEXT
                      )
                      """

clinical_services_table = """CREATE TABLE IF NOT EXISTS clinical_services (
                             id TEXT PRIMARY KEY,
                             value_set_id TEXT,
                             code TEXT,
                             code_system TEXT,
                             display TEXT,
                             version TEXT
                             )
                             """


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
        print("Failed to retrieve data:", response.status_code)
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
        time.sleep(3)  # TODO: find better way to make sure service waits
    except (BuildError, APIError) as e:
        print(f"An error occurred while starting the Docker service: {str(e)}")
    return container


def load_ersd_schema(ports: dict):
    """
    Loads the ersd.json to the message-parser endpoint to use to parse eRSD
    :param ports: port for the message-parser endpoint URL

    TODO: This does not currently seem to work; I can see the config loaded
    but I cannot seem to get parse-message to work with it.
    Issue to be resolved in future message-parser ticket fix.
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
    with open("seed-scripts/config/ersd.json", "r") as json_file:
        ersd_schema = json.load(json_file)
    url = f"http://localhost:{list(ports.values())[0]}/parse_message"
    headers = {"Content-Type": "application/json"}
    payload = {
        "message_format": "fhir",
        "message": data,
        "parsing_schema": ersd_schema,  # see load_ersd_schema, need to debug
        # "parsing_schema_name": "ersd.json"
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
    unique (i.e., the number  of unique ids matches number of rows).
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


def create_table(
    connection: sqlite3.Connection,
    table_name: str,
    sql_query: str,
    insert_rows: List[List[str]],
):
    """
    Takes the sqlite3 connection to delete existing table, initalize table,
    then insert data created in other data steps into the table

    :param connection: sqlite3 connection
    :param table_name: name of the table
    :param sql_query: sql query to create table, initalize columns
    :param insert_rows: list of lists of values to insert into table
    """
    cursor = connection.cursor()
    try:
        # drop existing table
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        # create initial rows for table
        cursor.execute(sql_query)
        # insert rows into table by looping through list of lists
        values = ", ".join("?" for _ in insert_rows[0])
        for row in insert_rows:
            cursor.execute(
                f"""
                        INSERT OR REPLACE into {table_name} VALUES ({values})
                        """,
                row,
            )
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        connection.rollback()
    finally:
        connection.commit()


def main():
    """
    Runs all the functions to:
    1. Load eRSD data json from APHL API.
    2. Start up message-parser.
    3. Post ersd.json message-parser parsing schema (WIP).
    4. Post eRSD data json to message-parser to get parsed data.
    5. Spin down message-parser.
    6. Use parsed data to create list of lists for each table.
    7. Load each table to sqlite3 database.
    """
    # extract and transform eRSD data
    ersd_data = load_ersd(ERSD_URL)

    # use message-parser to parse eRSD data, then spin down service
    container = start_docker_service(dockerfile_path, tag, ports)
    load_ersd_schema(ports)
    parsed_data = parse_ersd(ports, ersd_data)
    if container:
        container.stop()
        container.remove()

    # used parsed data to create needed tables as list of lists
    value_set_type_list = build_value_set_type_table(parsed_data)
    clinical_services_dict = build_clinical_services_dict(parsed_data)
    value_sets_list = build_value_sets_table(parsed_data, clinical_services_dict)
    conditions_list = build_conditions_table(parsed_data)
    clinical_services_list = build_clinical_services_table(parsed_data)

    # Create tables in eRSD database
    with sqlite3.connect("seed-scripts/ersd.db") as conn:
        create_table(conn, "value_set_type", value_set_type_table, value_set_type_list)
        create_table(conn, "value_sets", value_sets_table, value_sets_list)
        create_table(conn, "conditions", conditions_table, conditions_list)
        create_table(
            conn, "clinical_services", clinical_services_table, clinical_services_list
        )


if __name__ == "__main__":
    main()
