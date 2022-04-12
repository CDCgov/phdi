import logging

import azure.functions as func

from IntakePipeline.transform import transform_bundle
from IntakePipeline.linkage import add_patient_identifier
from IntakePipeline.fhir import (
    read_fhir_bundles,
    upload_bundle_to_fhir_server,
    store_bundle,
    get_fhirserver_cred_manager,
)

from config import get_required_config

from phdi_transforms.geo import get_smartystreets_client


def run_pipeline():
    salt = get_required_config("HASH_SALT")
    geocoder = get_smartystreets_client(
        get_required_config("SMARTYSTREETS_AUTH_ID"),
        get_required_config("SMARTYSTREETS_AUTH_TOKEN"),
    )
    fhirserver_cred_manager = get_fhirserver_cred_manager(
        get_required_config("FHIR_URL")
    )

    container_url = get_required_config("INTAKE_CONTAINER_URL")
    container_prefix = get_required_config("INTAKE_CONTAINER_PREFIX")
    output_path = get_required_config("OUTPUT_CONTAINER_PATH")

    for bundle in read_fhir_bundles(container_url, container_prefix):
        transform_bundle(geocoder, bundle)
        add_patient_identifier(salt, bundle)
        store_bundle(container_url, output_path, bundle)
        upload_bundle_to_fhir_server(fhirserver_cred_manager, bundle)


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Triggering intake pipeline")
    try:
        run_pipeline()
    except Exception:
        logging.exception("exception caught while running the intake pipeline")
        return func.HttpResponse(
            "error while running the intake pipeline", status_code=500
        )

    return func.HttpResponse("pipeline run successfully")
