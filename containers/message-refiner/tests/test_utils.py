from app.utils import create_clinical_services_dict


def test_create_clinical_services_dict():
    clinical_services_list = [
        {
            "dxtc": [
                {
                    "codes": ["U07.1", "U07.2"],
                    "system": "http://hl7.org/fhir/sid/icd-10-cm",
                },
                {
                    "codes": ["138389411000119105", "1119302008"],
                    "system": "http://snomed.info/sct",
                },
            ],
            "lrtc": [{"codes": ["95423-0", "96764-6"], "system": "http://loinc.org"}],
        }
    ]

    expected_output = {
        "icd10": ["U07.1", "U07.2"],
        "snomed": ["138389411000119105", "1119302008"],
        "loinc": ["95423-0", "96764-6"],
    }

    output = create_clinical_services_dict(clinical_services_list)
    assert output == expected_output
