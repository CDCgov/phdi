import io
import json
import logging
import os
#from ssl import enum_certificates

import azure.functions as func
from azure.storage.blob import ContainerClient

from Transform.fhir import get_patient_records

def transform_name(raw: str) -> str:
    """trim spaces, capitalize, etc"""
    raw = [x for x in raw if not x.isnumeric()]
    raw = ''.join(raw)
    raw = raw.upper()
    raw = raw.strip()
    return raw


def transform_phone(raw: str) -> str:
    """Make sure it's 10 digits, remove everything else"""
    raw = [x for x in raw if x.isnumeric()]
    raw = ''.join(raw)
    if len(raw) != 10:
        raw = None
    return raw

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
        # Transform names
        for i, name in enumerate(patient['name']):
            raw_last_name = name['family']
            patient['name'][i]['family'] = transform_name(raw_last_name)
            for j, raw_given_name in enumerate(name['given']):
                patient['name'][i]['given'][j] = transform_name(raw_given_name)
        #Transform phone numbers
        for i, phone_number in enumerate(patient['telecom']):
            raw_phone_number = phone_number['value']
            patient['telecom'][i]['value'] = transform_phone(raw_phone_number)
        print(patient)

    return func.HttpResponse("ok")