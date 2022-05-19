import logging
from typing import Dict

import azure.functions as func
from azure.core.exceptions import ResourceExistsError

from config import get_required_config

from phdi_building_blocks.azure_blob import store_data

from phdi_building_blocks.fhir import (
    upload_bundle_to_fhir_server,
    generate_filename,
    get_fhirserver_cred_manager,
)
from phdi_building_blocks.conversion import (
    convert_batch_messages_to_list,
    convert_message_to_fhir,
    get_file_type_mappings,
)

from phdi_building_blocks.geo import get_smartystreets_client, geocode_patient_address
from phdi_building_blocks.standardize import (
    standardize_patient_name,
    standardize_patient_phone,
)
from phdi_building_blocks.linkage import add_patient_identifier


def run_pipeline(
    message: str,
    message_mappings: Dict[str, str],
    fhir_url: str,
    access_token: str,
) -> None:
    """
    This function takes in a single message and attempts to convert, transform, and
    store the output to blob storage and the FHIR server.

    If the incoming message cannot be converted, it is stored to the configured
    invalid blob container and no further processing is done.
    """
    salt = get_required_config("HASH_SALT")
    geocoder = get_smartystreets_client(
        get_required_config("SMARTYSTREETS_AUTH_ID"),
        get_required_config("SMARTYSTREETS_AUTH_TOKEN"),
    )
    container_url = get_required_config("INTAKE_CONTAINER_URL")
    valid_output_path = get_required_config("VALID_OUTPUT_CONTAINER_PATH")
    invalid_output_path = get_required_config("INVALID_OUTPUT_CONTAINER_PATH")

    response = convert_message_to_fhir(
        message=message,
        filename=message_mappings["filename"],
        input_data_type=message_mappings["input_data_type"],
        root_template=message_mappings["root_template"],
        template_collection=message_mappings["template_collection"],
        access_token=access_token,
        fhir_url=fhir_url,
    )

    if response and response.get("resourceType") == "Bundle":
        bundle = response
        standardize_patient_name(bundle)
        standardize_patient_phone(bundle)
        geocode_patient_address(bundle, geocoder)

        add_patient_identifier(bundle, salt)
        try:
            store_data(
                container_url,
                valid_output_path,
                f"{message_mappings['filename']}.fhir",
                message_mappings["bundle_type"],
                message_json=bundle,
            )
        except ResourceExistsError:
            logging.warning(
                "Attempted to store preexisting resource: "
                + f"{message_mappings['filename']}.fhir"
            )

        upload_bundle_to_fhir_server(bundle, access_token, fhir_url)
    else:
        try:
            # Store invalid message
            store_data(
                container_url,
                invalid_output_path,
                f"{message_mappings['filename']}.{message_mappings['file_suffix']}",
                message_mappings["bundle_type"],
                message=message,
            )
        except ResourceExistsError:
            logging.warning(
                "Attempted to store preexisting resource: "
                + f"{message_mappings['filename']}.{message_mappings['file_suffix']}"
            )
        try:
            # Store response information
            store_data(
                container_url,
                invalid_output_path,
                f"{message_mappings['filename']}.{message_mappings['file_suffix']}"
                + ".convert-resp",
                message_mappings["bundle_type"],
                message_json=response,
            )
        except ResourceExistsError:
            logging.warning(
                "Attempted to store preexisting resource: "
                + f"{message_mappings['filename']}.{message_mappings['file_suffix']}"
                + ".convert-resp"
            )


def main(blob: func.InputStream) -> None:
    """
    This is the main entry point for the IntakePipeline Azure function.
    It is responsible for splitting an incoming batch file (or individual message)
    into a list of individual messages.  Each individual message is passed to the
    processing pipeline.
    """
    logging.debug("Entering intake pipeline ")

    fhir_url = get_required_config("FHIR_URL")
    cred_manager = get_fhirserver_cred_manager(fhir_url)

    try:
        access_token = cred_manager.get_access_token()

        # VA sends \\u000b & \\u001c in real data, ignore for now
        messages = convert_batch_messages_to_list(
            blob.read().decode("utf-8", errors="ignore")
        )
        message_mappings = get_file_type_mappings(blob.name)

        for i, message in enumerate(messages):
            message_mappings["filename"] = generate_filename(blob.name, i)
            run_pipeline(message, message_mappings, fhir_url, access_token.token)
    except Exception:
        logging.exception("Exception occurred during IntakePipeline processing.")
