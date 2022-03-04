import io
import json
import logging
import os

import pymongo
import smartystreets_python_sdk.us_street

import azure.functions as func
from azure.storage.blob import ContainerClient

from Transform.fhir import get_patient_records, write_patient_records
from Transform.geo import get_smartystreets_client, cached_geocode
from Transform.transforms import transform_record


CACHE_EXPIRATION = 60 * 60 * 24 * 7  # seconds * minutes * hours * days = 1 week


def main(req: func.HttpRequest) -> func.HttpResponse:
    # Load ndjson from blob store into List[Dict]
    try:
        patients = get_patient_records(
            conn_str=os.environ.get("AZURE_STORAGE_CONNECTION_STRING"),
            container_name=os.environ.get("BRONZE_PATIENT_CONTAINER"),
        )
    except:
        logging.exception("error reading patient records")
        return func.HttpResponse("failed to read patient records", status_code=500)

    # Load the cache client
    try:
        conn = pymongo.MongoClient(os.environ.get("COSMOSDB_CONN_STRING"))
        cache = conn.cache.geocode
        cache.create_index("_ts", expireAfterSeconds=CACHE_EXPIRATION)
    except:
        logging.exception("error connecting to cosmos db")
        return func.HttpResponse("failed to connect to cache", status_code=500)

    # Load the geocoding client
    try:
        client = get_smartystreets_client(
            os.environ.get("SMARTYSTREETS_AUTH_ID"),
            os.environ.get("SMARTYSTREETS_AUTH_TOKEN"),
        )
    except:
        logging.exception("error connecting to smartystreets")
        return func.HttpResponse("failed to connect to smartystreets", status_code=500)

    # Transform name, phone, and location (via geocoder) for each patient record
    try:
        output = []
        for patient in patients:
            output.append(transform_record(cache, client, patient))
    except:
        logging.exception("failed to transform patient record")
        return func.HttpResponse("failed to transform patient record", status_code=500)

    try:
        write_patient_records(
            conn_str=os.environ.get("AZURE_STORAGE_CONNECTION_STRING"),
            container_name=os.environ.get("SILVER_PATIENT_CONTAINER"),
            patients=output,
        )
    except:
        logging.exception("error writing patient records")
        return func.HttpResponse("failed to write patient records", status_code=500)

    # Write the records out to a different blob store (as ndjson)
    return func.HttpResponse(f"{len(output)} records written")
