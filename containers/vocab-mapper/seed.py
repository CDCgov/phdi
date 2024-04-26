import ast
import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()
# key can be obtained here: https://ersd.aimsplatform.org/#/api-keys
ERSD_API_KEY = os.getenv("ERSD_API_KEY")
ERSD_URL = f"https://ersd.aimsplatform.org/api/ersd/v2specification?format=json&api-key={ERSD_API_KEY}"
# TODO: use python to start service
MESSAGE_PARSER_URL = "http://localhost:8085/"


def load_ersd(URL: str) -> json:
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


def load_ersd_schema(MESSAGE_PARSER_URL: str):
    """
    Loads the ersd.json to the message-parser endpoint to use to parse eRSD
    :param MESSAGE_PARSER_URL: message-parser endpoint URL

    TODO: This does not currently seem to work; I can see the config loaded
    but I cannot seem to get parse-message to work with it
    """
    with open("ersd.json", "r") as json_file:
        ersd_schema = json.load(json_file)
    # Create payload to upload the schema to message-parser
    url = MESSAGE_PARSER_URL + "schemas/ersd.json"
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


def get_clinical_services_types(data: json) -> json:
    """
    Loop through eRSD json bundle in order to create a small dictionary of
    each of the (currently) 6 service types as defined by APHL with an array
    of their respective value set urls.

    This is the only part of the eRSD json bundle where the service type is
    defined for each of the value sets, so this will be a

    :param data: eRSD json bundle
    :return: ca dictionary of each service types with an array of their
    respective value set urls
    """
    clinical_service_dict = {}
    for service_type in data.get("entry"):
        url = service_type.get("resource").get("url")
        if url.startswith("http://ersd.aimsplatform.org/fhir/ValueSet/"):
            id = service_type.get("fullUrl").split("/")[-1]
            vs = service_type["resource"]["compose"]["include"][0]["valueSet"]
            clinical_service_dict[id] = vs
    return clinical_service_dict


def parse_ersd(MESSAGE_PARSER_URL: str, data: json) -> json:
    """
    Takes the eRSD bundle and posts it to the message parser. This flattens the
    eRSD bundle to a flatter json that can be parsed.

    :param MESSAGE_PARSER_ENDPOINT: endpoint of message_parser to send data.
    :param data: eRSD json bundle
    :return: parsed message.
    """
    with open("ersd.json", "r") as json_file:
        ersd_schema = json.load(json_file)
    url = MESSAGE_PARSER_URL + "parse_message"
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


ersd_data = load_ersd(ERSD_URL)
load_ersd_schema(MESSAGE_PARSER_URL)
clinincal_service_dict = get_clinical_services_types(ersd_data)

"""
TODO: We will add functions / update parse_ersd
based on plan in #1683 ticket
We should be able to use the clinical services dict to create pared down
FHIR bundles of just the relevant ValueSets, which will also require
updating ersd.json
"""

parsed_data = parse_ersd(MESSAGE_PARSER_URL, ersd_data)


def clinical_services_table(data: json) -> list:
    """
    Look through eRSD json to create clinical_services table
    :param data: eRSD json
    :return: list
    """
    clinical_services = data.get("clinical_services")
    results = []
    for service in clinical_services:
        value_set_id = service.get("value_set_id")
        value_set_name = service.get("display")
        valueable_codes = ast.literal_eval(service.get("valueable_codes"))
        compose_codes = ast.literal_eval(service.get("compose_codes"))
        expansion_codes = ast.literal_eval(service.geT("expansion_codes"))
        if isinstance(valueable_codes, dict):  # one item, need to list it
            valueable_codes = [valueable_codes]
        # valueable codes
        for valueable_code in valueable_codes:
            code_system = valueable_code.get("coding")[0].get("system")
            code = valueable_code.get("coding")[0].get("code")
            display = valueable_code.get("text")
            id = f"{value_set_id}_{code}"
            result = {
                "id": id,
                "code": code,
                "code_system": code_system,
                "display": display,
                "value_set_id": value_set_id,
                "value_set_name": value_set_name,
            }
            results.append(result)
        # compose
        compose_code_version = compose_codes.get("version")
        compose_code_system = compose_codes.get("system")
        for compose_code in compose_codes.get("concept"):
            code = compose_code.get("code")
            display = compose_code.get("display")
            id = f"{value_set_id}_{code}"
            result = {
                "id": id,
                "code": code,
                "code_system": compose_code_system,
                "display": display,
                "version": compose_code_version,
                "value_set_id": value_set_id,
                "value_set_name": value_set_name,
            }
            results.append(result)
        for expansion_code in expansion_codes:
            code_system = expansion_code.get("system")
            code = expansion_code.get("code")
            display = expansion_code.get("text")
            version = expansion_code.get("version")
            id = f"{value_set_id}_{code}"
            result = {
                "id": id,
                "code": code,
                "code_system": code_system,
                "display": display,
                "version": version,
                "value_set_id": value_set_id,
                "value_set_name": value_set_name,
            }
            results.append(result)


# Scratch, old code, to be removed
# def conditions_to_csv(json_file_path, csv_file_path):
#     """_summary_

#     Args:
#         json_file_path (_type_): _description_
#         csv_file_path (_type_): _description_
#     """
#     # Open the JSON file
#     with open(json_file_path, "r") as json_file:
#         data = json.load(json_file)

#         # Open the CSV file for writing
#         with open(csv_file_path, mode="w", newline="") as csv_file:
#             fieldnames = [
#                 "id",
#                 "name",
#                 "title",
#                 "status",
#                 "description",
#                 "use_context_system",
#                 "use_context_code",
#                 "use_context_text",
#                 "system",
#                 "version",
#                 "code",
#                 "display",
#             ]
#             writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
#             writer.writeheader()

#             # Loop through each entry in the JSON data
#             for entry in data["entry"]:
#                 resource = entry.get("resource", {})
#                 # Base attributes
#                 id = resource.get("id", "")

#                 # Check if id starts with a number
#                 if id and id[0].isdigit():
#                     name = resource.get("name", "")
#                     title = resource.get("title", "")
#                     status = resource.get("status", "")
#                     description = resource.get("description", "")

#                     # Extract useContext details
#                     use_context = resource.get("useContext", [])
#                     use_context_system = ""
#                     use_context_code = ""
#                     use_context_text = ""
#                     if use_context:
#                         value_codeable = (
#                             use_context[0]
#                             .get("valueCodeableConcept", {})
#                             .get("coding", [])
#                         )
#                         if value_codeable:
#                             use_context_system = value_codeable[0].get("system", "")
#                             use_context_code = value_codeable[0].get("code", "")
#                             use_context_text = (
#                                 use_context[0]
#                                 .get("valueCodeableConcept", {})
#                                 .get("text", "")
#                             )

#                     # Handle compose.include
#                     includes = resource.get("compose", {}).get("include", [])
#                     for include in includes:
#                         system = include.get("system", "")
#                         version = include.get("version", "")
#                         for concept in include.get("concept", []):
#                             writer.writerow(
#                                 {
#                                     "id": id,
#                                     "name": name,
#                                     "title": title,
#                                     "status": status,
#                                     "description": description,
#                                     "use_context_system": use_context_system,
#                                     "use_context_code": use_context_code,
#                                     "use_context_text": use_context_text,
#                                     "system": system,
#                                     "version": version,
#                                     "code": concept.get("code", ""),
#                                     "display": concept.get("display", ""),
#                                 }
#                             )

#                     # Handle expansion.contains
#                     contains = resource.get("expansion", {}).get("contains", [])
#                     for contain in contains:
#                         system = contain.get("system", "")
#                         version = contain.get("version", "")
#                         writer.writerow(
#                             {
#                                 "id": id,
#                                 "name": name,
#                                 "title": title,
#                                 "status": status,
#                                 "description": description,
#                                 "use_context_system": use_context_system,
#                                 "use_context_code": use_context_code,
#                                 "use_context_text": use_context_text,
#                                 "system": system,
#                                 "version": version,
#                                 "code": contain.get("code", ""),
#                                 "display": contain.get("display", ""),
#                             }
#                         )


# def valuesets_to_csv(json_file_path, csv_file_path):
#     """_summary_

#     Args:
#         json_file_path (_type_): _description_
#         csv_file_path (_type_): _description_
#     """
#     # Open the JSON file
#     with open(json_file_path, "r") as json_file:
#         data = json.load(json_file)

#         # Open the CSV file for writing
#         with open(csv_file_path, mode="w", newline="") as csv_file:
#             fieldnames = [
#                 "id",
#                 "name",
#                 "title",
#                 "status",
#                 "value_version",
#                 "publisher",
#                 "date",
#                 "use_context_system",
#                 "use_context_code",
#                 "system",
#                 "version",
#                 "code",
#             ]
#             writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
#             writer.writeheader()

#             # Loop through each entry in the JSON data
#             for entry in data["entry"]:
#                 resource = entry.get("resource", {})
#                 # Base attributes
#                 id = resource.get("id", "")

#                 # Check if id starts with a letter
#                 if id and id[0].isalpha():
#                     name = resource.get("name", "")
#                     title = resource.get("title", "")
#                     status = resource.get("status", "")
#                     version = resource.get("version", "")
#                     publisher = resource.get("publisher", "")
#                     date = resource.get("date", "")

#                     # Handle use context details
#                     use_context_system = ""
#                     use_context_code = ""
#                     if resource.get("useContext"):
#                         use_context = resource["useContext"][0]
#                         use_context_system = use_context["code"]["system"]
#                         use_context_code = use_context["valueCodeableConcept"][
#                             "coding"
#                         ][0]["code"]

#                     # Handle compose.include
#                     includes = resource.get("compose", {}).get("include", [])
#                     for include in includes:
#                         for vs in include.get("valueSet", []):
#                             # Extract only the numerical identifier if the
#                             # valueSet URL is formatted as expected
#                             code = (
#                                 vs.split("/")[-1]
#                                 if vs.startswith(
#                                     "http://cts.nlm.nih.gov/fhir/ValueSet/"
#                                 )
#                                 else vs
#                             )
#                             writer.writerow(
#                                 {
#                                     "id": id,
#                                     "name": name,
#                                     "title": title,
#                                     "status": status,
#                                     "value_version": version,
#                                     "publisher": publisher,
#                                     "date": date,
#                                     "use_context_system": use_context_system,
#                                     "use_context_code": use_context_code,
#                                     "system": "",
#                                     "version": "",
#                                     "code": code,
#                                 }
#                             )
#                     # Handle expansion.contains
#                     contains = resource.get("expansion", {}).get("contains", [])
#                     for contain in contains:
#                         code = (
#                             contain.get("code", "").split("/")[-1]
#                             if contain.get("code", "").startswith(
#                                 "http://cts.nlm.nih.gov/fhir/ValueSet/"
#                             )
#                             else contain.get("code", "")
#                         )
#                         writer.writerow(
#                             {
#                                 "id": id,
#                                 "name": name,
#                                 "title": title,
#                                 "status": status,
#                                 "value_version": version,
#                                 "publisher": publisher,
#                                 "date": date,
#                                 "use_context_system": use_context_system,
#                                 "use_context_code": use_context_code,
#                                 "system": contain.get("system", ""),
#                                 "version": contain.get("version", ""),
#                                 "code": code,
#                             }
#                         )


# # Call the function to process the JSON and create the CSVs
# conditions_to_csv(file, conditions)
# valuesets_to_csv(file, values)
