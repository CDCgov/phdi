import logging
from typing import Dict

import azure.functions as func
from azure.core.exceptions import ResourceExistsError

from config import get_required_config

from phdi_building_blocks.azure import (
    store_data,
    AzureFhirServerCredentialManager,
)
from phdi_building_blocks.fhir import (
    upload_bundle_to_fhir_server,
    generate_filename,
)
from phdi_building_blocks.conversion import (
    convert_batch_messages_to_list,
    convert_message_to_fhir,
    get_file_type_mappings,
)

from phdi_building_blocks.geo import (
    get_smartystreets_client,
    geocode_patients,
)
from phdi_building_blocks.standardize import (
    standardize_patient_names,
    standardize_all_phones,
)
from phdi_building_blocks.linkage import add_patient_identifier


def run_pipeline(
    message: str,
    message_mappings: Dict[str, str],
    fhir_url: str,
    cred_manager: AzureFhirServerCredentialManager,
) -> None:
    """
    This function takes in a single message and attempts to convert it
    to FHIR, transform and standardize it, and finally store the result
    in a given blob storage container. The function also makes an
    import upload to the FHIR server with the finalized bundle. If the
    incoming message cannot be converted, it is stored to the configured
    invalid blob container and no further processing is done.

    :param message: The raw HL7 message to attempt conversion on
    :param message_mappings: Dictionary having the appropriate
        template mapping for the type of HL7 file being processed
    :param fhir_url: The url of the FHIR server to interact with
    :param access_token: The token that allows us to authenticate
        with blob storage and the FHIR server
    """
    salt = get_required_config("HASH_SALT")
    geocoder = get_smartystreets_client(
        get_required_config("SMARTYSTREETS_AUTH_ID"),
        get_required_config("SMARTYSTREETS_AUTH_TOKEN"),
    )
    container_url = get_required_config("INTAKE_CONTAINER_URL")
    valid_output_path = get_required_config("VALID_OUTPUT_CONTAINER_PATH")
    invalid_output_path = get_required_config("INVALID_OUTPUT_CONTAINER_PATH")

    # Attempt conversion to FHIR
    response = convert_message_to_fhir(
        message=message,
        filename=message_mappings["filename"],
        input_data_type=message_mappings["input_data_type"],
        root_template=message_mappings["root_template"],
        template_collection=message_mappings["template_collection"],
        cred_manager=cred_manager,
        fhir_url=fhir_url,
    )

    # TODO: Determine if we still need this code. At the moment, I believe it's
    # duplicating storage with no benefit.

    # We got a valid conversion so apply desired standardizations
    # sequentially and then add the linking identifier
    if response and response.get("resourceType") == "Bundle":
        bundle = response
        standardized_bundle = standardize_patient_names(bundle)
        standardized_bundle = standardize_all_phones(standardized_bundle)
        standardized_bundle = geocode_patients(standardized_bundle, geocoder)
        standardized_bundle = add_patient_identifier(standardized_bundle, salt)

        # Now store the data in the desired container
        try:
            store_data(
                container_url,
                valid_output_path,
                f"{message_mappings['filename']}.fhir",
                message_mappings["bundle_type"],
                message_json=standardized_bundle,
            )
        except ResourceExistsError:
            logging.warning(
                "Attempted to store preexisting resource: "
                + f"{message_mappings['filename']}.fhir"
            )

        # Don't forget to import the bundle to the FHIR server as well
        upload_bundle_to_fhir_server(standardized_bundle, cred_manager, fhir_url)

    # For some reason, the HL7/CCDA message failed to convert.
    # This might be failure to communicate with the FHIR server due to
    # access/authentication reasons, or potentially malformed timestamps
    # in the data
    else:
        try:
            # First attempt is storing the message directly in the
            # invalid messages container
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
            # Then, try to store the conversion response information
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
    This is the main entry point for the IntakePipeline function.
    It is responsible for splitting an incoming batch file (or individual message)
    into a list of individual messages.  Each individual message is passed to the
    processing pipeline.

    :param blob: The HL7 message to be processed
    """
    # Set up logging, retrieve configuration variables
    logging.debug("Entering intake pipeline ")
    fhir_url = get_required_config("FHIR_URL")
    cred_manager = AzureFhirServerCredentialManager(fhir_url)

    try:
        # VA sends \\u000b & \\u001c in real data, ignore for now
        messages = convert_batch_messages_to_list(
            blob.read().decode("utf-8", errors="ignore")
        )

        # Once we have the file type mappings, run through all
        # messages in the blob and send them down the pipeline
        message_mappings = get_file_type_mappings(blob.name)
        for i, message in enumerate(messages):
            message_mappings["filename"] = generate_filename(blob.name, i)
            run_pipeline(message, message_mappings, fhir_url, cred_manager)
    except Exception:
        logging.exception("Exception occurred during IntakePipeline processing.")
