import json
import pathlib

from phdi.fhir.linkage.link import add_patient_identifier
from phdi.fhir.linkage.link import add_patient_identifier_in_bundle
from phdi.linkage.link import generate_hash_str


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

    add_patient_identifier_in_bundle(bundle, "some-salt")
    expected = generate_hash_str("doe-19900101-", "some-salt")
    actual = bundle["entry"][0]["resource"]["identifier"][0]["value"]
    assert actual == expected


def test_add_patient_identifier_by_bundle_overwrite():
    salt_str = "super-legit-salt"

    incoming_bundle = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "linkage"
            / "patient_with_linking_id_bundle.json"
        )
    )

    plaintext = (
        "John-Tiberius-Shepard-2053-11-07-"
        + "1234 Silversun Strip Boston, Massachusetts 99999"
    )

    expected_new_identifier = {
        "value": generate_hash_str(plaintext, salt_str),
        "system": "urn:ietf:rfc:3986",
        "use": "temp",
    }

    add_patient_identifier_in_bundle(incoming_bundle, salt_str)
    assert len(incoming_bundle["entry"]) == 3
    for resource in incoming_bundle["entry"]:
        if resource["resource"]["resourceType"] == "Patient":
            assert len(resource["resource"]["identifier"]) == 2
            assert resource["resource"]["identifier"][-1] == expected_new_identifier


def test_patient_identifier_overwrite():
    salt_str = "super-legit-salt"

    incoming_bundle = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "linkage"
            / "patient_with_linking_id_bundle.json"
        )
    )

    plaintext = (
        "John-Tiberius-Shepard-2053-11-07-"
        + "1234 Silversun Strip Boston, Massachusetts 99999"
    )

    expected_new_identifier = {
        "value": generate_hash_str(plaintext, salt_str),
        "system": "urn:ietf:rfc:3986",
        "use": "temp",
    }

    for entry in incoming_bundle["entry"]:
        if entry["resource"]["resourceType"] == "Patient":
            resource = entry.get("resource")
            add_patient_identifier(resource, salt_str, True)
            assert len(resource["identifier"]) == 2
            assert resource["identifier"][-1] == expected_new_identifier
            break


def test_add_patient_identifier_by_bundle():
    salt_str = "super-legit-salt"

    incoming_bundle = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "linkage"
            / "patient_with_linking_id_bundle.json"
        )
    )

    plaintext = (
        "John-Tiberius-Shepard-2053-11-07-"
        + "1234 Silversun Strip Boston, Massachusetts 99999"
    )

    expected_new_identifier = {
        "value": generate_hash_str(plaintext, salt_str),
        "system": "urn:ietf:rfc:3986",
        "use": "temp",
    }

    new_bundle = add_patient_identifier_in_bundle(incoming_bundle, salt_str, False)
    assert new_bundle != incoming_bundle
    assert len(new_bundle["entry"]) == 3

    for resource in new_bundle["entry"]:
        if resource["resource"]["resourceType"] == "Patient":
            assert len(resource["resource"]["identifier"]) == 2
            assert resource["resource"]["identifier"][-1] == expected_new_identifier


def test_add_patient_identifier():
    salt_str = "super-legit-salt"

    incoming_bundle = json.load(
        open(
            pathlib.Path(__file__).parent.parent.parent
            / "assets"
            / "linkage"
            / "patient_with_linking_id_bundle.json"
        )
    )

    plaintext = (
        "John-Tiberius-Shepard-2053-11-07-"
        + "1234 Silversun Strip Boston, Massachusetts 99999"
    )

    expected_new_identifier = {
        "value": generate_hash_str(plaintext, salt_str),
        "system": "urn:ietf:rfc:3986",
        "use": "temp",
    }

    for entry in incoming_bundle["entry"]:
        if entry["resource"]["resourceType"] == "Patient":
            resource = entry.get("resource")
            new_resource = add_patient_identifier(resource, salt_str, False)
            assert len(new_resource["identifier"]) == 2
            assert new_resource["identifier"][-1] == expected_new_identifier
            assert new_resource != resource
            break
