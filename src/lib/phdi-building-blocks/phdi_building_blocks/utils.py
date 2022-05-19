from typing import List


def find_patient_resources(bundle: dict) -> List[dict]:
    """Grab patient resources out of the bundle, and return a reference"""
    return [
        r
        for r in bundle.get("entry")
        if r.get("resource").get("resourceType") == "Patient"
    ]
