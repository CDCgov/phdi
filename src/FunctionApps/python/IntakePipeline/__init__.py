import azure.functions as func
import logging

from azure.core.exceptions import ResourceExistsError
from typing import Dict

from IntakePipeline.transform import transform_bundle
from IntakePipeline.linkage import add_patient_identifier
from IntakePipeline.fhir import (
    upload_bundle_to_fhir_server,
    store_data,
    generate_filename,
    get_fhirserver_cred_manager,
)
from IntakePipeline.conversion import (
    convert_batch_messages_to_list,
    convert_message_to_fhir,
    get_file_type_mappings,
)
from config import get_required_config
from phdi_transforms.geo import get_smartystreets_client


def run_pipeline(
    message: str,
    message_mappings: Dict[str, str],
    fhir_url: str,
    access_token: str,
) -> None:
    """
    This function takes in a single message and runs it through the Data
    Transformation section of the PHDI VA Pilot Architecture diagram. If
    the message is successfully converted to FHIR, then it is processed
    through the remaining transformations (standardization & geocoding),
    and stored in both a storage container and the FHIR server. If it is
    not valid, it is routed to a storage container marked as invalid, and
    no further processing is done.
    """
    salt = get_required_config("HASH_SALT")
    geocoder = get_smartystreets_client(
        get_required_config("SMARTYSTREETS_AUTH_ID"),
        get_required_config("SMARTYSTREETS_AUTH_TOKEN"),
    )
    container_url = get_required_config("INTAKE_CONTAINER_URL")
    valid_output_path = get_required_config("VALID_OUTPUT_CONTAINER_PATH")
    invalid_output_path = get_required_config("INVALID_OUTPUT_CONTAINER_PATH")

    bundle = convert_message_to_fhir(
        message=message,
        filename=message_mappings["filename"],
        input_data_type=message_mappings["input_data_type"],
        root_template=message_mappings["root_template"],
        template_collection=message_mappings["template_collection"],
        access_token=access_token,
        fhir_url=fhir_url,
    )

    if bundle:
        transform_bundle(geocoder, bundle)
        add_patient_identifier(salt, bundle)
        try:
            store_data(
                container_url,
                valid_output_path,
                f"{message_mappings['filename']}.fhir",
                message_mappings["bundle_type"],
                bundle=bundle,
            )
        except ResourceExistsError:
            logging.warning(
                "Attempted to store preexisting resource: "
                + f"{message_mappings['filename']}.fhir"
            )

        upload_bundle_to_fhir_server(bundle, access_token, fhir_url)
    else:
        try:
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


def main(blob: func.InputStream) -> None:
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
