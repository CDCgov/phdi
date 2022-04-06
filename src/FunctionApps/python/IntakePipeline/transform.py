from smartystreets_python_sdk import us_street

from phdi_transforms.basic import transform_name, transform_phone
from phdi_transforms.geo import geocode


def find_patient_resources(bundle: dict) -> dict:
    """Grab patient resources out of the bundle, and return a reference"""
    return [
        r
        for r in bundle.get("entry")
        if r.get("resource").get("resourceType") == "Patient"
    ]


def transform_bundle(client: us_street.Client, bundle: dict) -> None:
    """Standardize name and phone, geocode the address"""

    for resource in find_patient_resources(bundle):
        patient = resource.get("resource")

        # Transform names
        for name in patient.get("name", []):
            if "family" in name:
                name["family"] = transform_name(name["family"])

            name["given"] = [transform_name(g) for g in name["given"]]

        # Transform phone numbers
        for telecom in patient.get("telecom", []):
            if telecom.get("system") == "phone" and "value" in telecom:
                telecom["value"] = transform_phone(telecom["value"])

        for address in patient.get("address", []):
            # Generate a one-line address to pass to the geocoder
            one_line = " ".join(address.get("line"))
            one_line += f" {address.get('city')}, {address.get('state')}"
            if "postalCode" in address and address["postalCode"]:
                one_line += f" {address['postalCode']}"

            geocoded = geocode(client, one_line)
            if geocoded:
                address["line"] = geocoded.address
                address["city"] = geocoded.city
                address["state"] = geocoded.state
                address["postalCode"] = geocoded.zipcode

                if "extension" not in address:
                    address["extension"] = []

                address["extension"].append(
                    {
                        "url": "http://hl7.org/fhir/StructureDefinition/geolocation",
                        "extension": [
                            {"url": "latitude", "valueDecimal": geocoded.lat},
                            {"url": "longitude", "valueDecimal": geocoded.lng},
                        ],
                    }
                )
