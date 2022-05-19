import azure.functions as func
import config
import json
import logging

from phdi_building_blocks import fhir


def main(req: func.HttpRequest) -> func.HttpResponse:
    fhir_url = config.get_required_config("FHIR_URL")

    poll_step = float(config.get_required_config("FHIR_EXPORT_POLL_INTERVAL", 30))
    poll_timeout = float(config.get_required_config("FHIR_EXPORT_POLL_TIMEOUT", 300))

    cred_manager = fhir.AzureFhirserverCredentialManager(fhir_url=fhir_url)

    access_token = cred_manager.get_access_token()

    try:
        export_response = fhir.export_from_fhir_server(
            access_token=access_token,
            fhir_url=fhir_url,
            export_scope=req.params.get("export_scope", ""),
            since=req.params.get("since", ""),
            resource_type=req.params.get("type", ""),
            poll_step=poll_step,
            poll_timeout=poll_timeout,
        )
        logging.debug(f"Export response received: {json.dumps(export_response)}")
    except Exception as exception:
        # Log and re-raise so it bubbles up as an execution failure
        logging.exception("Error occurred while performing export operation.")
        raise exception

    return func.HttpResponse(status_code=202)
