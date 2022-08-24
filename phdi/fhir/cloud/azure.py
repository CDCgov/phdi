import io

from azure.storage.blob import download_blob_from_url
from typing import Iterator, TextIO, Tuple

from phdi.cloud.azure import AzureCredentialManager


def download_from_fhir_export_response(
    export_response: dict,
    cred_manager: AzureCredentialManager,
) -> Iterator[Tuple[str, TextIO]]:
    """
    Accept the export response content as specified here:
    https://hl7.org/fhir/uv/bulkdata/export/index.html#response---complete-status

    Loops through the "output" array and yields the resource_type (e.g. Patient)
    along with TextIO wrapping ndjson content.

    :param export_response: JSON-type dictionary holding the response from
      the export URL the FHIR server set up
    :param cred_manager: Service used to get an access token used to make a request
    """
    # TODO: Handle error array that could be contained in the response content.

    for export_entry in export_response.get("output", []):
        resource_type = export_entry.get("type")
        blob_url = export_entry.get("url")

        yield (
            resource_type,
            _download_export_blob(blob_url=blob_url, cred_manager=cred_manager),
        )


def _download_export_blob(
    blob_url: str, cred_manager: AzureCredentialManager, encoding: str = "utf-8"
) -> TextIO:
    """
    Download an export file blob.

    :param blob_url: Blob URL location to download from blob storage
    :param cred_manager: Service used to get an access token used to make a request
    :param encoding: encoding to apply to the ndjson content, defaults to "utf-8"
    """
    bytes_buffer = io.BytesIO()
    azure_creds = cred_manager.get_credential_object()
    download_blob_from_url(
        blob_url=blob_url, output=bytes_buffer, credential=azure_creds
    )
    text_buffer = io.TextIOWrapper(buffer=bytes_buffer, encoding=encoding, newline="\n")
    text_buffer.seek(0)

    return text_buffer
