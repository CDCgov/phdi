import json
import logging
import os
import re

import redis
import requests
import azure.functions as func


CENSUS_URL = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
CACHE_EXPIRATION = 60 * 60 * 24 * 7  # seconds * minutes * hours * days = 1 week


def geocode(address: str, cache: redis.StrictRedis) -> dict[str, str]:
    # Normalize the address to a cache key
    key = "geocode::" + re.sub("[^A-Z0-9]", "", address.upper())
    cached = cache.get(key)
    if cached:
        return json.loads(cached)

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
    retval = {"lng": coords.get("x"), "lat": coords.get("y")}
    cache.setex(key, CACHE_EXPIRATION, json.dumps(retval))
    return retval


def main(req: func.HttpRequest) -> func.HttpResponse:
    if "address" not in req.params:
        return func.HttpResponse("address parameter is required", status_code=400)

    try:
        cache = redis.StrictRedis(
            host=os.environ.get("REDIS_HOST", "localhost"),
            port=int(os.environ.get("REDIS_PORT", "6379")),
            password=os.environ.get("REDIS_PASSWORD", ""),
            ssl=os.environ.get("REDIS_TLS", "0") == "1",
        )
    except:
        logging.exception("failed to connect to redis")

    try:
        address = req.params.get("address")
        result = geocode(address, cache)
        return func.HttpResponse(json.dumps(result), mimetype="application/json")
    except:
        logging.exception("error geocoding address")
        return func.HttpResponse("error", status_code=500)
