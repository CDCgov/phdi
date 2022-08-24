# Tutorials: The Linkage Module

This guide serves as a tutorial overview of the functionality available in both `linkage.py` and `fhir.linkage.py`. It will cover concepts such as using FHIR bundles for linkage, imports, and common use invocations.

## The Basics: How it links

The linkage module adds a patient identifier to each patient record in a bundle. The patient identifier is generated from patient information (name, birth date, and address), converting it to a hash string and adding a salt value. If two patient identifiers are the same, that means that the two patient records are referring to the same patient. 

## Common Uses
Listed below are several example use cases for employing the linkage module.

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
print(bundle)
```

Using the `True` tag in the third parameter overwrites your bundle with the new resource tag. This means that in the previous example, the `bundle` variable will be directly modified by add_patient_identifier. If using `False`, save the output to a variable. 
```
new_patient_bundle = add_patient_identifier(bundle, salt, False)
print(new_patient_bundle)
```

The bundle print will look like this:
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
                "identifier":[
                    {
                        "value":"fbe6f3b7430f53eb60074c906d3052f457283d9992d8a2526b8d32590db8a0fc", //new value
                        "system":"urn:ietf:rfc:3986",
                        "use":"temp"
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
        "value":"fbe6f3b7430f53eb60074c906d3052f457283d9992d8a2526b8d32590db8a0fc", //new value
        "system":"urn:ietf:rfc:3986",
        "use":"temp"
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
print(patient_hash)
>>> fbe6f3b7430f53eb60074c906d3052f457283d9992d8a2526b8d32590db8a0fc //some hash string
```

You can then save the patient_hash into your data type and compare with other hash to determine if they are equal. 