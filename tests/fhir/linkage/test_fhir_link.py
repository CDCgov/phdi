import json
import pathlib
from phdi.linkage.link import generate_hash_str
from phdi.fhir.linkage.link import add_patient_identifier


def test_missing_address():
    bundle = {
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "name": [{"family": "doe"}],
                    "birthDate": "19900101",
                }
            }
        ]
    }

    add_patient_identifier(bundle, "some-salt")
    expected = generate_hash_str("doe-19900101-", "some-salt")
    actual = bundle["entry"][0]["resource"]["identifier"][0]["value"]
    assert actual == expected


def test_add_patient_identifier():
    salt_str = "super-legit-salt"

    incoming_bundle = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "patient_with_linking_id_bundle.json"
        )
    )

    plaintext = (
        "John-Tiberius-Shepard-2053-11-07-"
        + "1234 Silversun Strip Zakera Ward, Citadel 99999"
    )

    expected_new_identifier = {
        "value": generate_hash_str(plaintext, salt_str),
        "system": "urn:ietf:rfc:3986",
        "use": "temp",
    }

    add_patient_identifier(incoming_bundle, salt_str)
    assert len(incoming_bundle["entry"]) == 3
    for resource in incoming_bundle["entry"]:
        if resource["resource"]["resourceType"] == "Patient":
            assert len(resource["resource"]["identifier"]) == 2
            assert resource["resource"]["identifier"][-1] == expected_new_identifier
