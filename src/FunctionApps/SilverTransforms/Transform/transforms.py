import pymongo
import smartystreets_python_sdk.us_street

from Transform.fhir import get_patient_records
from Transform.geo import cached_geocode


def transform_name(raw: str) -> str:
    """trim spaces, capitalize, etc"""
    raw = [x for x in raw if not x.isnumeric()]
    raw = "".join(raw)
    raw = raw.upper()
    raw = raw.strip()
    return raw


def transform_phone(raw: str) -> str:
    """Make sure it's 10 digits, remove everything else"""
    raw = [x for x in raw if x.isnumeric()]
    raw = "".join(raw)
    if len(raw) != 10:
        raw = None
    return raw


def transform_record(
    cache: pymongo.collection.Collection,
    client: smartystreets_python_sdk.us_street.Client,
    patient: dict,
) -> dict:

    # Transform names
    for i, name in enumerate(patient["name"]):
        raw_last_name = name["family"]
        patient["name"][i]["family"] = transform_name(raw_last_name)
        for j, raw_given_name in enumerate(name["given"]):
            patient["name"][i]["given"][j] = transform_name(raw_given_name)

    # Transform phone numbers
    for i, phone_number in enumerate(patient["telecom"]):
        raw_phone_number = phone_number["value"]
        patient["telecom"][i]["value"] = transform_phone(raw_phone_number)

    for i, address in enumerate(patient.get("address", [])):
        # Generate a one-line address to pass to the geocoder
        one_line = " ".join(address.get("line"))
        one_line += f" {address.get('city')}, {address.get('state')} {address.get('postalCode')}"
        geocoded = cached_geocode(cache, client, one_line)
        if geocoded:
            patient["address"][i] = {
                "line": geocoded["address"],
                "city": geocoded["city"],
                "state": geocoded["state"],
                "extension": [
                    {
                        "url": "http://hl7.org/fhir/StructureDefinition/geolocation",
                        "extension": [
                            {"url": "latitude", "valueDecimal": geocoded["lat"]},
                            {"url": "longitude", "valueDecimal": geocoded["lng"]},
                        ],
                    }
                ],
            }

    return patient
