import io
from typing import Iterator
from typing import TextIO
from typing import Tuple

from azure.storage.blob import download_blob_from_url

from phdi.cloud.azure import AzureCredentialManager


def download_from_fhir_export_response(
    export_response: dict,
    cred_manager: AzureCredentialManager,
) -> Iterator[Tuple[str, TextIO]]:
    """
    Accepts the export response content as specified here:
    https://hl7.org/fhir/uv/bulkdata/export/index.html#response---complete-status

    Loops through the "output" array and yields the resource_type (e.g., Patient)
    along with TextIO wrapping ndjson content.

    :param export_response: A dictionary holding the final export response.
    :param cred_manager: The credential manager used to authenticate to the
      storage account.
    :return: An iterator of tuples. Each tuple is comprised of:

      * FHIR resource type (str)
      * Export file content (io.TextIO)
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
    Downloads an export file blob.

    :param blob_url: The blob URL location to download from blob storage.
    :param cred_manager: The credential manager used to authenticate to the
      storage account.
    :param encoding: The character encoding to apply to the downloaded content.
      Default: utf-8
    :return: Content of export file located at `blob_url`
    """
    bytes_buffer = io.BytesIO()
    azure_creds = cred_manager.get_credential_object()
    download_blob_from_url(
        blob_url=blob_url, output=bytes_buffer, credential=azure_creds
    )
    text_buffer = io.TextIOWrapper(buffer=bytes_buffer, encoding=encoding, newline="\n")
    text_buffer.seek(0)

    return text_buffer
