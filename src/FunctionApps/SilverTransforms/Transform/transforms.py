import pymongo
import smartystreets_python_sdk.us_street

from Transform.geo import cached_geocode

from phdi_transforms.basic import transform_name, transform_phone


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
        one_line += f" {address.get('city')}, {address.get('state')}"
        if "postalCode" in address and address["postalCode"]:
            one_line += f" {address['postalCode']}"

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
