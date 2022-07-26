import azure.functions as func
import config
import json
import logging
import requests

from phdi import fhir
from phdi.azure import AzureFhirServerCredentialManager


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Main function that activates the FHIR export function app utility.
    An HTTP request is used to kick off the procedure. For more information,
    see the README file accompanying the FhirServerExport function app.

    :param req: The request initiating a FHIR export.
    :return: The response from the FHIR server
    """

    # Load configurations and environment variables
    fhir_url = config.get_required_config("FHIR_URL")
    poll_step = float(config.get_required_config("FHIR_EXPORT_POLL_INTERVAL", 30))
    poll_timeout = float(config.get_required_config("FHIR_EXPORT_POLL_TIMEOUT", 300))
    container = config.get_required_config("FHIR_EXPORT_CONTAINER", "fhir-exports")
    if container == "<none>":
        container = ""

    cred_manager = AzureFhirServerCredentialManager(fhir_url=fhir_url)

    # Properly configured, kickoff the export procedure
    try:
        export_response = fhir.export_from_fhir_server(
            cred_manager=cred_manager,
            fhir_url=fhir_url,
            export_scope=req.params.get("export_scope", ""),
            since=req.params.get("since", ""),
            resource_type=req.params.get("type", ""),
            container=container,
            poll_step=poll_step,
            poll_timeout=poll_timeout,
        )
        logging.debug(f"Export response received: {json.dumps(export_response)}")

    except requests.HTTPError as exception:
        logging.exception(
            f"Error occurred while making reqeust to {exception.request.url}, "
            + f"status code: {exception.response.status_code}"
        )

    except Exception as exception:
        # Log and re-raise so it bubbles up as an execution failure
        logging.exception("Error occurred while performing export operation.")
        raise exception

    return func.HttpResponse(status_code=202)
