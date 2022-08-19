# Tutorials: The Linkage Module

This guide serves as a tutorial overview of the functionality available in both `linkage.py` and `fhir.linkage.py`. It will cover concepts such as data type basics, imports, and common uses invocations.

## The Basics: How it links

The linkage module adds a patient identifier to each patient record in a bundle. If two hash strings are the same, that means that the two patient records are referring to the same patient. The hash string generation is a straightforward name and address combination. 

## Common Uses
Listed below are several example use cases for employing the geospatial module.

### Passing in a FHIR Bundle of Patient Data
Suppose you had a FHIR bundle that had the following data

```
{
    "resourceType": "Bundle",
    ...
    "entry": [
        {
            "fullUrl": "ajshdfo8ashf8191hf",
            "resource": {
                "resourceType": "Patient",
                "id": "65489-asdf5-6d8w2-zz5g8",
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
                        "postalCode": "99999"
                    }
                ]
            }
        }
    ]
}
```

To add patient identifiers to the bundle, you can use the `add_patient_identifier` function in the FHIR linkage package

```
from phdi.fhir.linkage.link import add_patient_identifier

bundle = {...your bundle here...}
salt = 'some-salt-string'

add_patient_identifier(bundle, salt, True)
```

Using the `True` tag overwrites your bundle with the new resource tag, if using `False`, save the output to a variable
```
new_patient_bundle = add_patient_identifier(bundle, salt, False)
```

The bundle should now look like this:
```
{
    "resourceType": "Bundle",
    ...
    "entry": [
        {
            "fullUrl": "ajshdfo8ashf8191hf",
            "resource": {
                "resourceType": "Patient",
                "id": "65489-asdf5-6d8w2-zz5g8",
                "identifier": [
                    {
                        "value": "new-hash-string", 
                        "type": {
                            "coding": [
                                {
                                    "code": "real-code",
                                    "system": "a-real-url"
                                }
                            ]
                        },
                        "system": "urn:oid:1.2.840.114350.1.13.163.3.7.2.696570"
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
                        "postalCode": "99999"
                    }
                ]
            }
        }
        ...
    ]
}
```

The key section that was added is the `identifier` section: 
```
"identifier": [
    {
        "value": "new-hash-string", 
        "type": {
            "coding": [
                {
                    "code": "real-code",
                    "system": "a-real-url"
                }
            ]
        },
        "system": "urn:oid:1.2.840.114350.1.13.163.3.7.2.696570"
    }
]
```

### Using your own non-FHIR data type 
If you did not want to use the FHIR bundle data type, you can just use `generate_hash_str` on a patient's name, DOB, and address.

```
from phdi.linkage.link import generate_hash_str

patient_name = 'foo bar'
patient_dob = '01/01/2001'
patient_address = '1234 foobar street`

patient_combined = f'{patient_name}{patient_dob}{patient_address}'
salt_str = 'some-salt-string

patient_hash = generate_hash_str(patient_combined, salt_str)

```

You can then save the patient_hash into your data type and compare with other hash to determine if they are equal. 