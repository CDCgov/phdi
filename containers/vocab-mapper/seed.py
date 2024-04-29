import ast
import json
import os
import sqlite3
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

load_dotenv()
# eRSD constants, can be obtained at: https://ersd.aimsplatform.org/#/api-keys
ERSD_API_KEY = os.getenv("ERSD_API_KEY")
ERSD_URL = f"https://ersd.aimsplatform.org/api/ersd/v2specification?format=json&api-key={ERSD_API_KEY}"

# python constants to start message-parser service
dockerfile_path = Path(__file__).parent.parent / "message-parser"
tag = "message-parser:latest"
ports = {"8080": 8080}

# SQL queries to initialize each table we need
value_set_type_table = """CREATE TABLE IF NOT EXISTS value_set_type (
                          id TEXT PRIMARY KEY,
                          clinical_service_type TEXT
                       )
                       """

value_sets_table = """CREATE TABLE IF NOT EXISTS value_sets (
                      id TEXT,
                      condition_code TEXT,
                      condition_code_system TEXT,
                      value_set_name TEXT,
                      author TEXT,
                      clinical_service_type_id
                      )
                      """
clinical_services_table = """CREATE TABLE IF NOT EXISTS clinical_services (
                             id TEXT,
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
        print(f"Building Docker image with tag '{tag}'...")
        client.images.build(path=str(dockerfile_path), tag=tag)
        print("Image built successfully.")
        print("Running container...")
        container = client.containers.run(tag, ports=ports, detach=True)
        time.sleep(15)  # TODO: find better way to make sure service waits
        print(f"Container started successfully: {container.id}")
    except (BuildError, APIError) as e:
        print(f"An error occurred while starting the Docker service: {str(e)}")
    return container


def load_ersd_schema(ports: dict):
    """
    Loads the ersd.json to the message-parser endpoint to use to parse eRSD
    :param ports: port for the message-parser endpoint URL

    TODO: This does not currently seem to work; I can see the config loaded
    but I cannot seem to get parse-message to work with it
    """
    with open("ersd.json", "r") as json_file:
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
    with open("ersd.json", "r") as json_file:
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


def build_value_set_type_table(data: dict) -> Tuple[dict, List[List[str]]]:
    """
    Loop through eRSD json bundle in order to build a small table of
    each of the (currently) 6 service types as defined by APHL with its id
    and short description of the clinical service type.

    This is the only part of the eRSD json bundle where the service type is
    defined for each of the value sets, so this function also produces a small
    dictionary that has each value_set_id as a key with its service type id.

    :param data: eRSD json bundle
    :return: a dictionary of each value_set URL with its service type as value,
             a list of lists of the id and type of each of the service types
             to load to a database
    """
    clinical_services_dict = {}
    value_set_type_table = []
    for service_type in data.get("entry"):
        url = service_type.get("resource").get("url")
        # right now, the 6 service types are the only ones that start with
        # this URL. One other option could be to look for a id that is a
        # 4-character, lowercase alpha (sdtc). However, regex tends to be slow.
        if url.startswith("http://ersd.aimsplatform.org/fhir/ValueSet/"):
            id = service_type.get("fullUrl").split("/")[-1]
            vs = service_type["resource"]["compose"]["include"][0]["valueSet"]
            type = service_type.get("resource").get("title")
            value_set_type_table.append([id, type])
            for value in vs:
                clinical_services_dict[value.split("/")[-1]] = id
    return clinical_services_dict, value_set_type_table


def build_value_sets_table(data: dict, clinical_services_dict: dict) -> List[List[str]]:
    """
    Look through eRSD json to create value sets table, where the primary key
    is the value_set_id that contains the name and codes for each service.

    It also uses the clinical services dictionary that will have the clinical
    service type for each of the services.

    :param data: message-parser parsed eRSD json
    :param clinical_services_dict: a dictionary of each value_set URL with its
    service type as value
    :return: list of lists of for each of the value set id, name, and code info
    """
    clinical_services = data.get("clinical_services")
    value_set_list = []
    for service in clinical_services:
        value_set_id = service.get("value_set_id")
        value_set_name = service.get("display")
        valueable_codes = ast.literal_eval(service.get("valueable_codes"))
        if isinstance(valueable_codes, dict):  # one item, need to list it
            valueable_codes = [valueable_codes]
        # valueable codes to build value_set
        for valueable_code in valueable_codes:
            code_system = valueable_code.get("coding")[0].get("system")
            code = valueable_code.get("coding")[0].get("code")
            result = [
                value_set_id,
                code,
                code_system,
                value_set_name,
                "",  # what is author?
                clinical_services_dict[value_set_id],
            ]
            value_set_list.append(result)
    return value_set_list


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
        expansion_codes = ast.literal_eval(service.get("expansion_codes"))
        if isinstance(compose_codes, dict):  # one item, need to list it
            compose_codes = [compose_codes]
        if isinstance(expansion_codes, dict):
            expansion_codes = [expansion_codes]
        # compose codes to build clinical_services
        for compose_code in compose_codes:
            version = compose_code.get("version", "")
            system = compose_code.get("system", "")
            for concept in compose_code.get("concept"):
                code = concept.get("code", "")
                display = concept.get("display", "")
                id = f"{value_set_id}_{code}"
                result = [id, value_set_id, code, version, display, system]
                clinical_services_list.append(result)
        # expansion codes to extend clinical_services
        # right now, expansion is purely duplicative, and lacks display.
        for expansion_code in expansion_codes:
            system = expansion_code.get("system", "")
            code = expansion_code.get("code", "")
            display = expansion_code.get("text", "")
            version = expansion_code.get("version", "")
            id = f"{value_set_id}_{code}"
            result = [id, value_set_id, code, version, display, system]
            clinical_services_list.append(result)
    return clinical_services_list


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


# extract and transform eRSD data, use raw data to transform for one table
ersd_data = load_ersd(ERSD_URL)
clinical_services_dict, value_set_type_list = build_value_set_type_table(ersd_data)

# start message-parser service and parse data
# TODO: We should be able to use clinical services dict to create pared down
# FHIR bundles of just the relevant ValueSets, which will also require
# updating ersd.json.
# For now, building off existing work of just parsing whole json; opportunity
# for future refinement.
# use message-parser to parse eRSD data, then two transform data for two tables
# run message-parser services
container = start_docker_service(dockerfile_path, tag, ports)
load_ersd_schema(ports)
parsed_data = parse_ersd(ports, ersd_data)
print("Tasks completed inside Docker.")
if container:  # stop and remove once work complete
    container.stop()
    container.remove()
    print(f"Container {container.id} stopped and removed.")


# TODO: We will need to still add functions
# that clean/check each of the list of lists before loading
# for example, clinical_service.compose and clinical_service.expansion
# are VERY duplicative, so we will likely want to do some pre-cleaning
# and in general just have checks to confirm uniqueness of each table's pkey
value_set_list = build_value_sets_table(parsed_data, clinical_services_dict)
clinical_service_list = build_clinical_services_table(parsed_data)

# Create tables in eRSD database
conn = sqlite3.connect("ersd.db")
create_table(conn, "value_set_type", value_set_type_table, value_set_type_list)
create_table(conn, "value_sets", value_sets_table, value_set_list)
create_table(conn, "clinical_services", clinical_services_table, clinical_service_list)
conn.close()
