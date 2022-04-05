from unittest import mock
from IntakePipeline.linkage import generate_hash_str
from IntakePipeline.linkage import add_patient_identifier
from IntakePipeline.utils import get_required_config

TEST_ENV = {
    "HASH_SALT": "super-secret-definitely-legit-passphrase"
}

@mock.patch.dict("os.environ", TEST_ENV)
def test_generate_hash():

    salt_str = get_required_config('HASH_SALT')

    patient_1 = "John-Shepard-2153/11/07-1234 Silversun Strip Zakera Ward Citadel 99999"
    patient_2 = "Tali-Zora-Vas-Normandy-2160/05/14-PO Box 1 Rock Rannoch"
    patient_3 = "John-Shepard-2183/11/07-1234 Silversun Strip Zakera Ward Citadel 99998"

    hash_1 = generate_hash_str(salt_str, patient_1)
    hash_2 = generate_hash_str(salt_str, patient_2)
    hash_3 = generate_hash_str(salt_str, patient_3)

    assert(hash_1 != hash_2)
    assert(hash_2 != hash_3)
    assert(hash_1 != hash_3)


@mock.patch('IntakePipeline.linkage.generate_hash_str')
@mock.patch.dict("os.environ", TEST_ENV)
def test_add_patient_identifier(patched_hash_str):

    salt_str = get_required_config('HASH_SALT')
    patched_hash_str.return_value = "1234567890abcdef"

    incoming_bundle = {
        "resourceType": "Bundle",
        "type": "batch",
        "timestamp": "2022-01-01T00:00:30",
        "identifier": {
            "value": "a-totally-legit-id"
        },
        "id": "45bdc851-2fe5-cf8a-2fd7-dd24b23409e4",
        "entry": [
            {
                "fullUrl": "asdfasdfu2189u812",
                "resource": {
                    "resourceType": "MessageHeader",
                    "resourceBody": "some-FHIR-stuff"
                }
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
                            "given": [
                            "John",
                            "Tiberius"
                            ],
                            "use": "official"
                        }
                    ],
                    "birthDate": "2053-11-07",
                    "gender": "male",
                    "address": [
                        {
                            "line": [
                            "1234 Silversun Strip"
                            ],
                            "city": "Zakera Ward",
                            "state": "Citadel",
                            "postalCode": "99999",
                        }
                    ]
                }
            },
            {
                "fullUrl": "64a6s87df98a46e8a52d",
                "resource": {
                    "resourceType": "Provenance",
                    "resourceBody": "moar-FHIR-stuff"
                }
            }
        ]
    }

    expected_new_identifier = {
        'value': patched_hash_str.return_value,
        'system': 'urn:ietf:rfc:3986',
        'use': 'temp'
    }

    add_patient_identifier(salt_str, incoming_bundle)
    patched_hash_str.assert_called_once()
    assert len(incoming_bundle['entry']) == 3
    for resource in incoming_bundle['entry']:
        if resource['resource']['resourceType'] == 'Patient':
            assert len(resource['resource']['identifier']) == 2
            assert resource['resource']['identifier'][-1] == expected_new_identifier