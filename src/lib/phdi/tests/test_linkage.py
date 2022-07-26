from phdi_building_blocks.linkage import (
    generate_hash_str,
    add_patient_identifier,
)
import json
import pathlib


def test_generate_hash():

    salt_str = "super-legit-salt"
    patient_1 = "John-Shepard-2153/11/07-1234 Silversun Strip Zakera Ward Citadel 99999"
    patient_2 = "Tali-Zora-Vas-Normandy-2160/05/14-PO Box 1 Rock Rannoch"

    hash_1 = generate_hash_str(patient_1, salt_str)
    hash_2 = generate_hash_str(patient_2, salt_str)

    assert hash_1 == "0aa5aa1f6183a24670b2e1848864514e119ae6ca63bb35246ef215e7a0746a35"
    assert hash_2 == "102818c623290c24069beb721c6eb465d281b3b67ecfb6aef924d14affa117b9"


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
            pathlib.Path(__file__).parent
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
