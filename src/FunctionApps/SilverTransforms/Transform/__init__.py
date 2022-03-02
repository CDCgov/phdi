import io
import json
import logging
import os

import azure.functions as func
from azure.storage.blob import ContainerClient

from Transform.fhir import get_patient_records


def transform_name(raw: str) -> str:
    """trim spaces, capitalize, etc"""
    return raw.upper()


def transform_phone(raw: str) -> str:
    """Make sure it's 10 digits, remove everything else"""
    pass


def main(req: func.HttpRequest) -> func.HttpResponse:
    # Load ndjson from blob store into List[Dict]
    # Transform each record
    #   Name standardization
    #   Phone number standardization
    #   Maybe date standardization
    #   Geocoding home address (to lat/lng and canonical address)
    # Write the records out to a different blob store (as ndjson)
    patients = get_patient_records(
        conn_str=os.environ.get("AZURE_STORAGE_CONNECTION_STRING"),
        container_name=os.environ.get("PATIENT_BUNDLE_CONTAINER"),
    )

    for patient in patients:
        print(patient)

    return func.HttpResponse("ok")
