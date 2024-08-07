import dataclasses
import datetime
import json
import pathlib
import re
import uuid
from functools import cache
from pathlib import Path
from typing import Literal
from typing import Union

import fhirpathpy
import requests
from fastapi import status
from frozendict import frozendict
from lxml import etree as ET

from app.cloud.azure import AzureCredentialManager
from app.cloud.core import BaseCredentialManager
from app.cloud.gcp import GcpCredentialManager
from app.config import get_settings
from app.fhir.transport import http_request_with_reauth
from app.phdc.models import Address
from app.phdc.models import Name
from app.phdc.models import Observation
from app.phdc.models import Organization
from app.phdc.models import Patient
from app.phdc.models import PHDCInputData
from app.phdc.models import Telecom
from app.transport.http import http_request_with_retry

DIBBS_REFERENCE_SIGNIFIER = "#REF#"


@cache
def load_parsing_schema(schema_name: str) -> dict:
    """
    Load a parsing schema given its name. Look in the 'custom_schemas/' directory first.
    If no custom schemas match the provided name, check the schemas provided by default
    with this service in the 'default_schemas/' directory.

    :param path: The path to an extraction schema file.
    :return: A dictionary containing the extraction schema.
    """
    custom_schema_path = Path(__file__).parent / "custom_schemas" / schema_name
    try:
        with open(custom_schema_path, "r") as file:
            parsing_schema = json.load(file)
    except FileNotFoundError:
        try:
            default_schema_path = (
                Path(__file__).parent / "default_schemas" / schema_name
            )
            with open(default_schema_path, "r") as file:
                parsing_schema = json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"A schema with the name '{schema_name}' could not be found."
            )

    return freeze_parsing_schema(parsing_schema)


def freeze_parsing_schema(parsing_schema: dict) -> frozendict:
    """
    Given a parsing schema dictionary, freeze it and all of its nested dictionaries
    into a single immutable dictionary.

    :param parsing_schema: A dictionary containing a parsing schema.
    :return: A frozen dictionary containing the parsing schema.
    """
    return freeze_parsing_schema_helper(parsing_schema)


def freeze_parsing_schema_helper(schema: dict) -> frozendict:
    """
    Given a parsing schema dictionary, freeze it and all of its nested dictionaries.

    :param schema: A dictionary containing a parsing schema.
    :return: A frozen dictionary containing the parsing schema.
    """
    if isinstance(schema, dict):
        for key, value in schema.items():
            if isinstance(value, dict):
                schema[key] = freeze_parsing_schema_helper(value)
        return frozendict(schema)


# Using frozendict here to have an immutable that can be hashed for caching purposes.
# Caching the parsers reduces parsing time by over 60% after the first request for a
# given schema.
@cache
def get_parsers(extraction_schema: frozendict) -> frozendict:
    """
    Generate a FHIRpath parser for each field in a given schema. Return these parsers as
    values in a dictionary whose keys indicate the field in the schema the parser is
    associated with.

    :param extraction_schema: A dictionary containing an extraction schema.
    :return: A dictionary containing a FHIRpath parsers for each field in the provided
    schema.
    """
    parsers = {}

    for field, field_definition in extraction_schema.items():
        parser = {}
        parser["primary_parser"] = fhirpathpy.compile(field_definition["fhir_path"])
        if "secondary_schema" in field_definition:
            secondary_parsers = {}
            for secondary_field, secondary_field_definition in field_definition[
                "secondary_schema"
            ].items():
                # Base case: secondary field is located on this resource
                if not secondary_field_definition["fhir_path"].startswith("Bundle"):
                    if (
                        "secondary_schema" in secondary_field_definition
                        and secondary_field_definition["secondary_schema"] is not None
                    ):
                        tertiary_parser = {}
                        tertiary_parsers = {}
                        tertiary_parser["primary_parser"] = fhirpathpy.compile(
                            secondary_field_definition["fhir_path"]
                        )
                        for (
                            tertiary_field,
                            tertiary_field_definition,
                        ) in secondary_field_definition["secondary_schema"].items():
                            tertiary_parsers[tertiary_field] = {
                                "secondary_fhir_path": fhirpathpy.compile(
                                    tertiary_field_definition["fhir_path"]
                                )
                            }
                        secondary_parsers[secondary_field] = {
                            "primary_parser": tertiary_parser["primary_parser"],
                            "secondary_parsers": tertiary_parsers,
                        }

                    else:
                        secondary_parsers[secondary_field] = {
                            "secondary_fhir_path": fhirpathpy.compile(
                                secondary_field_definition["fhir_path"]
                            )
                        }
                # Reference case: secondary field is located on a different resource,
                # so we can't compile the fhir_path proper; instead, compile the
                # reference for quick access later
                else:
                    secondary_parsers[secondary_field] = {
                        "secondary_fhir_path": secondary_field_definition["fhir_path"],
                        "reference_path": fhirpathpy.compile(
                            secondary_field_definition["reference_lookup"]
                        ),
                    }
            parser["secondary_parsers"] = secondary_parsers
        parsers[field] = parser
    return frozendict(parsers)


def get_metadata(parsed_values: dict, schema) -> dict:
    """
    Given a dictionary of parsed values and a schema, creates a dictionary containing
    metadata for each field in the parsed values dictionary.

    :param parsed_values: A dictionary containing parsed values.
    :param schema: A dictionary containing a schema.
    :return: A dictionary containing metadata for each field in the parsed values
    """
    data = {}
    for key, value in parsed_values.items():
        if key not in schema:
            data[key] = field_metadata(value=value)
        else:
            fhir_path = schema[key]["fhir_path"] if "fhir_path" in schema[key] else ""
            match = re.search(r"resourceType\s*=\s*'([^']+)'", fhir_path)
            resource_type = match.group(1) if match and match.group(1) else ""
            data_type = schema[key]["data_type"] if "data_type" in schema[key] else ""
            metadata = schema[key]["metadata"] if "metadata" in schema[key] else {}
            data[key] = field_metadata(
                value=value,
                fhir_path=fhir_path,
                data_type=data_type,
                resource_type=resource_type,
                metadata=metadata,
            )
    return data


def field_metadata(
    value: str = "",
    fhir_path: str = "",
    data_type: str = "",
    resource_type: str = "",
    metadata: dict = {},
) -> dict:
    """
    Given metadata for a field, creates a dictionary containing that metadata.

    :param value: The value of the field.
    :param fhir_path: The FHIR path of the field.
    :param data_type: The data type of the field.
    :param resource_type: The resource type of the field.
    :param metadata: Additional metadata for the field.
    :return: A dictionary containing the metadata for the field.
    """
    data = {
        "value": value,
        "fhir_path": fhir_path,
        "data_type": data_type,
        "resource_type": resource_type,
    }
    for key, key_value in metadata.items():
        data[key] = key_value
    return data


def search_for_required_values(input: dict, required_values: list) -> str:
    """
    Search for required values in the input dictionary and the environment.
    Found in the environment not present in the input dictionary that are found in the
    environment are added to the dictionary. A message is returned indicating which,
    if any, required values could not be found.

    :param input: A dictionary potentially originating from the body of a POST request
    :param required_values: A list of values to search for in the input dictionary and
    the environment.
    :return: A string message indicating if any required values could not be found and
    if so which ones.
    """

    missing_values = []

    for value in required_values:
        if input.get(value) in [None, ""]:
            if get_settings().get(value) is None:
                missing_values.append(value)
            else:
                input[value] = get_settings()[value]

    message = "All values were found."
    if missing_values != []:
        message = (
            "The following values are required, but were not included in the request "
            "and could not be read from the environment. Please resubmit the request "
            "including these values or add them as environment variables to this "
            f"service. missing values: {', '.join(missing_values)}."
        )

    return message


def convert_to_fhir(
    message: str,
    message_type: Literal["elr", "vxu", "ecr"],
    fhir_converter_url: str,
    headers: dict = {},
    credential_manager: BaseCredentialManager = None,
) -> requests.Response:
    """
    Convert a message to FHIR by making a request to an instance of the DIBBs FHIR
    conversion service.

    :param message: The serialized contents of the message to be converted to FHIR.
    :param message_type: The type of the message.
    :param fhir_converter_url: The URL of an instance of the FHIR conversion service.
    :return:

    """
    conversion_settings = {
        "elr": {"input_type": "hl7v2", "root_template": "ORU_R01"},
        "vxu": {"input_type": "hl7v2", "root_template": "VXU_V04"},
        "ecr": {"input_type": "ecr", "root_template": "EICR"},
    }

    data = {
        "input_data": message,
        "input_type": conversion_settings[message_type]["input_type"],
        "root_template": conversion_settings[message_type]["root_template"],
    }
    fhir_converter_url = fhir_converter_url + "/convert-to-fhir"
    if credential_manager:
        access_token = credential_manager.get_access_token()
        headers["Authorization"] = f"Bearer {access_token}"
        response = http_request_with_reauth(
            credential_manager=credential_manager,
            url=fhir_converter_url,
            retry_count=3,
            request_type="POST",
            allowed_methods=["POST"],
            headers=headers,
            data=data,
        )
    else:
        response = http_request_with_retry(
            url=fhir_converter_url,
            retry_count=3,
            request_type="POST",
            allowed_methods=["POST"],
            headers=headers,
            data=data,
        )

    return response


credential_managers = {"azure": AzureCredentialManager, "gcp": GcpCredentialManager}


def get_credential_manager(
    credential_manager: str, location_url: str = None
) -> BaseCredentialManager:
    """
    Return a credential manager for different cloud providers depending upon which
    one the user requests via the parameter.

    :param credential_manager: A string identifying which cloud credential
    manager is desired.
    :return: Either a Google Cloud Credential Manager or an Azure Credential Manager
    depending upon the value passed in.
    """
    credential_manager_class = credential_managers.get(credential_manager)
    result = None
    # if the credential_manager_class is not none then instantiate an instance of it
    if credential_manager_class is not None:
        if credential_manager == "azure":
            result = credential_manager_class(resource_location=location_url)
        else:
            result = credential_manager_class()

    return result


def read_json_from_assets(filename: str) -> dict:
    """
    Reads a JSON file from the assets directory.

    :param filename: The name of the file to read.
    :return: A dictionary containing the contents of the file.
    """
    return json.load(open((pathlib.Path(__file__).parent.parent / "assets" / filename)))


def read_file_from_assets(filename: str) -> str:
    """
    Reads a file from the assets directory.

    :param filename: The name of the file to read.
    :return: A string containing the contents of the file.
    """
    with open(
        (pathlib.Path(__file__).parent.parent / "assets" / filename), "r"
    ) as file:
        return file.read()


def get_datetime_now() -> datetime.datetime:
    """
    Gets the current date and time.

    :return: A datetime object representing the current date and time.
    """
    return datetime.datetime.now()


def clean_schema(schema: dict):
    """
    Recursively remove any 'secondary_schema' fields that are None or empty.
    :param schema: the parsing schema dictionary to clean out
    """
    keys_to_delete = []
    for key, value in schema.items():
        if isinstance(value, dict):
            clean_schema(value)  # Recursively clean nested dictionaries
            if "secondary_schema" in value and not value["secondary_schema"]:
                keys_to_delete.append("secondary_schema")
        elif value is None:
            keys_to_delete.append(key)

    for key in keys_to_delete:
        del schema[key]


def extract_and_apply_parsers(parsing_schema, message, response):
    """
    Helper function used to pull parsing methods for each field out of the
    passed-in schema, resolve any reference dependencies, and apply the
    result to the input FHIR bundle. If reference dependencies are present
    (e.g. an Observation resource that references an ordering provider
    Organization), this function will raise an error if those references
    cannot be resolved (if the ID of the referenced object can't be found,
    for example).

    :param parsing_schema: A dictionary holding the parsing schema send
      to the endpoint.
    :param message: The FHIR bundle to extract values from.
    :param response: The Response object the endpoint will send back, in
      case we need to apply error status codes.
    :return: A dictionary mapping schema keys to parsed values.
    """
    parsers = get_parsers(parsing_schema)
    parsed_values = {}

    # Iterate over each parser and make the appropriate path call
    for field, parser in parsers.items():
        if "secondary_parsers" not in parser:
            value = parser["primary_parser"](message)
            if len(value) == 0:
                value = None
            else:
                value = ",".join(map(str, value))
            parsed_values[field] = value

        # Use the secondary field data structure, remembering that some
        # fhir paths might not be compiled yet
        else:
            initial_values = parser["primary_parser"](message)
            values = []

            # This check allows us to use secondary schemas on fields that
            # are just datatype structs, rather than full arrays. This is
            # useful when we want multiple fields of information from a
            # referenced resource, but there's only one instance of the
            # resource type referencing another resource in the bundle
            # (e.g. we want multiple values about the Bundle's Custodian:
            # bundle.custodian is a dict with a reference, so we only need
            # to find that reference once)
            if not isinstance(initial_values, list):
                initial_values = [initial_values]

            for initial_value in initial_values:
                value = {}
                for secondary_field, secondary_path_struct in parser[
                    "secondary_parsers"
                ].items():
                    if "reference_path" not in secondary_path_struct:
                        # Check for tertiary values
                        if "secondary_parsers" in secondary_path_struct:
                            tertiary_parser = secondary_path_struct["primary_parser"]
                            tertiary_values = []
                            for v in tertiary_parser(initial_value):
                                tv = {}
                                for (
                                    tertiary_field,
                                    tertiary_path_struct,
                                ) in secondary_path_struct["secondary_parsers"].items():
                                    tv_parser = tertiary_path_struct[
                                        "secondary_fhir_path"
                                    ]
                                    if len(tv_parser(v)) == 0:
                                        tv[tertiary_field] = None
                                    else:
                                        tv[tertiary_field] = ",".join(
                                            map(str, tv_parser(v))
                                        )
                                tertiary_values.append(tv)
                            value[secondary_field] = tertiary_values
                        else:
                            try:
                                secondary_parser = secondary_path_struct[
                                    "secondary_fhir_path"
                                ]
                                if len(secondary_parser(initial_value)) == 0:
                                    value[secondary_field] = None
                                else:
                                    value[secondary_field] = ",".join(
                                        map(str, secondary_parser(initial_value))
                                    )
                            # By default, fhirpathpy will compile such that *only*
                            # actual resources can be accessed, rather than data types.
                            # This is fine for most cases, but sometimes the actual data
                            # we want is in a list of structs rather than a list of
                            # resources, such as a list of patient addresses. This
                            # exception catches that and allows an ordinary property
                            # search.
                            except KeyError:
                                try:
                                    accessors = (
                                        secondary_parser.parsedPath.get("children")[0]
                                        .get("text")
                                        .split(".")[1:]
                                    )
                                    val = initial_value
                                    for acc in accessors:
                                        if "[" not in acc:
                                            val = val[acc]
                                        else:
                                            sub_acc = acc.split("[")[1].split("]")[0]
                                            val = val[acc.split("[")[0].strip()][
                                                int(sub_acc)
                                            ]
                                    value[secondary_field] = str(val)
                                except:  # noqa
                                    value[secondary_field] = None

                    # Reference case: information is contained on another
                    # resource that we have to look up
                    else:
                        reference_parser = secondary_path_struct["reference_path"]
                        if len(reference_parser(initial_value)) == 0:
                            response.status_code = status.HTTP_400_BAD_REQUEST
                            return {
                                "message": "Provided `reference_lookup` location does "
                                "not point to a referencing identifier",
                                "parsed_values": {},
                            }
                        else:
                            reference_to_find = ",".join(
                                map(str, reference_parser(initial_value))
                            )

                            # FHIR references are prefixed with resource type
                            reference_to_find = reference_to_find.split("/")[-1]

                            # Build the resultant concatenated reference path
                            reference_path = secondary_path_struct[
                                "secondary_fhir_path"
                            ].replace(DIBBS_REFERENCE_SIGNIFIER, reference_to_find)
                            reference_path = fhirpathpy.compile(reference_path)
                            referenced_value = reference_path(message)
                            if len(referenced_value) == 0:
                                value[secondary_field] = None
                            else:
                                value[secondary_field] = ",".join(
                                    map(str, referenced_value)
                                )

                values.append(value)
            parsed_values[field] = values
    return parsed_values


def transform_to_phdc_input_data(parsed_values: dict) -> PHDCInputData:
    """
    Transform the parsed values into a PHDCInputData object.

    :param parsed_values: A dictionary containing the values parsed out of a FHIR
        bundle.
    :return: A PHDCInputData object.
    """
    # Translate to internal data classes
    input_data = PHDCInputData()
    input_data.patient = Patient()
    input_data.organization = Organization()
    for key, value in parsed_values.items():
        match key:
            case "patient_address":
                input_data.patient.address = [Address(**address) for address in value]
            case "patient_name":
                input_data.patient.name = [Name(**name) for name in value]
            case "patient_administrative_gender_code":
                input_data.patient.administrative_gender_code = value
            case "patient_birth_time":
                input_data.patient.birth_time = value
            case "patient_race_code":
                input_data.patient.race_code = value
            case "patient_ethnic_group_code":
                input_data.patient.ethnic_group_code = value
            case "observations":
                observation_groups = {
                    "social-history": input_data.social_history_info,
                    "EXPOS": input_data.repeating_questions,
                    "clinical_info": input_data.clinical_info,
                    "vital-signs": input_data.clinical_info,
                }
                for obs in value:
                    observation_type = "clinical_info"
                    if obs["obs_type"] in observation_groups:
                        observation_type = obs["obs_type"]

                    observation_groups[observation_type].append([Observation(**obs)])

                    if "components" in obs and obs["components"] is not None:
                        components = []
                        for component in obs["components"]:
                            components.append(Observation(**component))
                        observation_groups[observation_type].append(components)

            case "custodian_represented_custodian_organization":
                organizations = []
                address_fields = set([f.name for f in dataclasses.fields(Address)])

                for entry in value:
                    organizations.append(
                        Organization(
                            name=entry["name"],
                            id=str(uuid.uuid4()),
                            address=Address(
                                **dict(
                                    filter(
                                        lambda e: e[0] in address_fields, entry.items()
                                    )
                                )
                            ),
                            telecom=Telecom(value=entry["phone"]),
                        )
                    )

                input_data.organization = organizations
            case _:
                pass
    return input_data


def get_phdc_section(
    section_title: Literal[
        "SOCIAL HISTORY INFORMATION",
        "Clinical Information",
        "REPEATING QUESTIONS",
        "header",
    ],
    tree: ET.ElementTree,
) -> Union[ET.Element, ET.ElementTree]:
    """
    Returns the specified section of a PHDC from a file.

    :param section_title: The section of the PHDC
    :param tree: The ElementTree fromwhich to parse the section.
    :return: A section Element containing the contents of the file per the
    section_title.
    """
    # Remove the namespaces
    root = tree.getroot()
    for elem in root.getiterator():
        elem.tag = ET.QName(elem).localname
    ET.cleanup_namespaces(root)

    if section_title == "header":
        # Remove components
        for component in root.findall("component"):
            root.remove(component)

        return root
    else:
        for component in root:
            if component.tag == "component":
                for c in component:
                    if c.tag == "structuredBody":
                        for sb in c:
                            for section in sb:
                                for title in section:
                                    if title.text == section_title:
                                        return sb
