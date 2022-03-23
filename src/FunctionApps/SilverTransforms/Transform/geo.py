import re


from pymongo.collection import Collection
from smartystreets_python_sdk import us_street
from phdi_transforms.geo import geocode, GeocodeResult


def cached_geocode(
    cache: Collection, client: us_street.Client, address: str
) -> GeocodeResult:

    ckey = re.sub("[^A-Z0-9]", "", address.upper())
    cached = cache.find_one({"key": ckey})
    if cached:
        del cached["key"]
        return cached

    resp = geocode(client, address)

    if resp:
        cache.insert_one(resp | {"key": ckey})

    return resp
