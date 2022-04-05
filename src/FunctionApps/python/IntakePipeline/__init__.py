import logging

import azure.functions as func

from IntakePipeline.transform import transform_bundle
from IntakePipeline.linkage import add_patient_identifier
from IntakePipeline.fhir import read_fhir_bundles, upload_bundle_to_fhir_server
from IntakePipeline.utils import get_required_config

from phdi_transforms.geo import get_smartystreets_client


def run_pipeline():
    salt = get_required_config("HASH_SALT")
    geocoder = get_smartystreets_client(
        get_required_config("SMARTYSTREETS_AUTH_ID"),
        get_required_config("SMARTYSTREETS_AUTH_TOKEN"),
    )

    for bundle in read_fhir_bundles(
        get_required_config("INTAKE_CONTAINER_URL"),
        get_required_config("INTAKE_CONTAINER_PREFIX"),
    ):
        transform_bundle(geocoder, bundle)
        add_patient_identifier(salt, bundle)
        upload_bundle_to_fhir_server(bundle)


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
