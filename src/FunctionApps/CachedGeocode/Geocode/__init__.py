import json
import logging
import os
import re

import pymongo
import requests
import azure.functions as func


CENSUS_URL = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
CACHE_EXPIRATION = 60 * 60 * 24 * 7  # seconds * minutes * hours * days = 1 week


def geocode(address: str, cache: pymongo.collection.Collection) -> dict[str, str]:
    # Normalize the address to a cache key
    key = re.sub("[^A-Z0-9]", "", address.upper())
    cached = cache.find_one({"key": key})
    if cached:
        return cached

    # Grab the result from the census api
    resp = requests.get(
        CENSUS_URL,
        params={"benchmark": "Public_AR_Current", "format": "json", "address": address},
    )

    if not resp.ok:
        logging.exception(
            f"census request failed code={resp.status_code} text={resp.text}"
        )
        raise Exception("census request failed")

    coords = resp.json().get("result", {}).get("addressMatches")[0].get("coordinates")
    doc = {"key": key, "lng": coords.get("x"), "lat": coords.get("y")}
    cache.insert_one(doc)
    return doc


def main(req: func.HttpRequest) -> func.HttpResponse:
    if "address" not in req.params:
        return func.HttpResponse("address parameter is required", status_code=400)

    try:
        conn = pymongo.MongoClient(os.environ.get("COSMOSDB_CONN_STRING"))

        # connect to the cache 'db' and the geocode 'collection'
        cache = conn.cache.geocode

        # we should only need to do this once per collection
        cache.create_index("_ts", expireAfterSeconds=CACHE_EXPIRATION)
    except Exception:
        logging.exception("failed to connect to cosmos db")

    try:
        address = req.params.get("address")
        result = geocode(address, cache)
        return func.HttpResponse(
            json.dumps({"lat": result.get("lat"), "lng": result.get("lng")}),
            mimetype="application/json",
        )
    except Exception:
        logging.exception("error geocoding address")
        return func.HttpResponse("error", status_code=500)
