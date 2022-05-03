from smartystreets_python_sdk import us_street
from typing import List
from phdi_transforms.basic import transform_name, transform_phone
from phdi_transforms.geo import geocode


def find_patient_resources(bundle: dict) -> List[dict]:
    """Grab patient resources out of the bundle, and return a reference"""
    return [
        r
        for r in bundle.get("entry")
        if r.get("resource").get("resourceType") == "Patient"
    ]


def process_name(name: dict, patient: dict) -> None:
    """
    Given a patient's collection of names, the patient resource itself, and
    a specification for whether to track changes via standardization, apply
    transforms to the patient's given and family names and store whether
    the transformed results are different in extension information.
    """
    if "family" in name:
        std_family = transform_name(name["family"])
        raw_family = name["family"]
        patient["extension"].append(
            {
                "url": "http://usds.gov/fhir/phdi/StructureDefinition/family-name-was-standardized",  # noqa
                "valueBoolean": raw_family != std_family,
            }
        )
        name["family"] = std_family

    if "given" in name:
        std_givens = [transform_name(g) for g in name["given"]]
        raw_givens = [g for g in name["given"]]
        any_diffs = any(
            [raw_givens[i] != std_givens[i] for i in range(len(raw_givens))]
        )
        patient["extension"].append(
            {
                "url": "http://usds.gov/fhir/phdi/StructureDefinition/given-name-was-standardized",  # noqa
                "valueBoolean": any_diffs,
            }
        )
        name["given"] = std_givens


def transform_bundle(client: us_street.Client, bundle: dict) -> None:
    """Standardize name and phone, geocode the address"""

    for resource in find_patient_resources(bundle):
        patient = resource.get("resource")
        if "extension" not in patient:
            patient["extension"] = []

        # Transform names
        for name in patient.get("name", []):
            process_name(name, patient)

        # Transform phone numbers
        raw_phones = []
        std_phones = []
        for telecom in patient.get("telecom", []):
            if telecom.get("system") == "phone" and "value" in telecom:
                transformed_phone = transform_phone(telecom["value"])
                raw_phones.append(telecom["value"])
                std_phones.append(transformed_phone)
                telecom["value"] = transformed_phone
        any_diffs = len(raw_phones) != len(std_phones) or any(
            [raw_phones[i] != std_phones[i] for i in range(len(raw_phones))]
        )
        patient["extension"].append(
            {
                "url": "http://usds.gov/fhir/phdi/StructureDefinition/phone-was-standardized",  # noqa
                "valueBoolean": any_diffs,
            }
        )

        raw_addresses = []
        std_addresses = []
        for address in patient.get("address", []):
            # Generate a one-line address to pass to the geocoder
            one_line = " ".join(address.get("line", []))
            one_line += f" {address.get('city')}, {address.get('state')}"
            if "postalCode" in address and address["postalCode"]:
                one_line += f" {address['postalCode']}"
            raw_addresses.append(one_line)

            geocoded = geocode(client, one_line)
            std_one_line = ""
            if geocoded:
                address["line"] = geocoded.address
                address["city"] = geocoded.city
                address["state"] = geocoded.state
                address["postalCode"] = geocoded.zipcode
                std_one_line = f"{geocoded.address} {geocoded.city}, {geocoded.state} {geocoded.zipcode}"  # noqa
                std_addresses.append(std_one_line)

                if "extension" not in address:
                    address["extension"] = []

                address["extension"].append(
                    {
                        "url": "http://hl7.org/fhir/StructureDefinition/geolocation",  # noqa
                        "extension": [
                            {"url": "latitude", "valueDecimal": geocoded.lat},
                            {"url": "longitude", "valueDecimal": geocoded.lng},
                        ],
                    }
                )
        any_dffs = (len(raw_addresses) != len(std_addresses)) or any(
            [raw_addresses[i] != std_addresses[i] for i in range(len(raw_addresses))]
        )
        patient["extension"].append(
            {
                "url": "http://usds.gov/fhir/phdi/StructureDefinition/address-was-standardized",  # noqa
                "valueBoolean": any_dffs,
            }
        )
