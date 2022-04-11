from IntakePipeline.linkage import generate_hash_str
from IntakePipeline.linkage import add_patient_identifier


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

    add_patient_identifier("some-salt", bundle)
    expected = generate_hash_str("doe-19900101-", "some-salt")
    actual = bundle["entry"][0]["resource"]["identifier"][0]["value"]
    assert actual == expected


def test_add_patient_identifier():
    salt_str = "super-legit-salt"

    incoming_bundle = {
        "resourceType": "Bundle",
        "type": "batch",
        "timestamp": "2022-01-01T00:00:30",
        "identifier": {"value": "a-totally-legit-id"},
        "id": "45bdc851-2fe5-cf8a-2fd7-dd24b23409e4",
        "entry": [
            {
                "fullUrl": "asdfasdfu2189u812",
                "resource": {
                    "resourceType": "MessageHeader",
                    "resourceBody": "some-FHIR-stuff",
                },
            },
            {
                "fullUrl": "ajshdfo8ashf8191hf",
                "resource": {
                    "resourceType": "Patient",
                    "id": "65489-asdf5-6d8w2-zz5g8",
                    "identifier": [
                        {
                            "value": "99999",
                            "type": {
                                "coding": [
                                    {
                                        "code": "real-code",
                                        "system": "a-real-url",
                                    }
                                ]
                            },
                            "system": "urn:oid:1.2.840.114350.1.13.163.3.7.2.696570",
                        }
                    ],
                    "name": [
                        {
                            "family": "Shepard",
                            "given": ["John", "Tiberius"],
                            "use": "official",
                        }
                    ],
                    "birthDate": "2053-11-07",
                    "gender": "male",
                    "address": [
                        {
                            "line": ["1234 Silversun Strip"],
                            "city": "Zakera Ward",
                            "state": "Citadel",
                            "postalCode": "99999",
                        }
                    ],
                },
            },
            {
                "fullUrl": "64a6s87df98a46e8a52d",
                "resource": {
                    "resourceType": "Provenance",
                    "resourceBody": "moar-FHIR-stuff",
                },
            },
        ],
    }

    plaintext = (
        "John-Tiberius-Shepard-2053-11-07-"
        + "1234 Silversun Strip Zakera Ward, Citadel 99999"
    )

    expected_new_identifier = {
        "value": generate_hash_str(plaintext, salt_str),
        "system": "urn:ietf:rfc:3986",
        "use": "temp",
    }

    add_patient_identifier(salt_str, incoming_bundle)
    assert len(incoming_bundle["entry"]) == 3
    for resource in incoming_bundle["entry"]:
        if resource["resource"]["resourceType"] == "Patient":
            assert len(resource["resource"]["identifier"]) == 2
            assert resource["resource"]["identifier"][-1] == expected_new_identifier
