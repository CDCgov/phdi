import logging

import azure.functions as func

from IntakePipeline.transform import transform_bundle
from IntakePipeline.linkage import add_patient_identifier
from IntakePipeline.fhir import read_fhir_bundles, upload_bundle_to_fhir_server


def run_pipeline():
    for bundle in read_fhir_bundles():
        transform_bundle(bundle)
        add_patient_identifier(bundle)
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
