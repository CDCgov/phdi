import httpx
import pytest

TCR_URL = "http://0.0.0.0:8080"
STAMP_ENDPOINT = TCR_URL + "/stamp-condition-extensions"


@pytest.fixture
def fhir_bundle(read_json_from_test_assets):
    return read_json_from_test_assets("sample_ecr.json")


@pytest.mark.integration
def test_health_check(setup):
    health_check_response = httpx.get(TCR_URL)
    assert health_check_response.status_code == 200


@pytest.mark.integration
def test_tcr_stamping(setup, fhir_bundle):
    reportable_condition_code = "840539006"
    request = {"bundle": fhir_bundle, "conditions": [reportable_condition_code]}
    stamp_response = httpx.post(STAMP_ENDPOINT, json=request)
    assert stamp_response.status_code == 200

    # There are two resources that should be stamped:
    #   1. the COVID diagnosis observation
    #   2. the observation containing a positive COVID test
    expected_stamped_ids = [
        "d90b3a5e-3328-48dd-bcbb-3c810a0ffb3d",
        "a73bcca9-c9e9-7ea2-44c4-b271b9017284",
    ]
    stamped_resources = []
    stamped_bundle = stamp_response.json().get("extended_bundle")
    for entry in stamped_bundle.get("entry", []):
        resource = entry.get("resource")

        # Check whether we stamped this resource for the final comparison
        extensions = resource.get("extension", [])
        for ext in extensions:
            if ext == {
                "url": "https://reportstream.cdc.gov/fhir/StructureDefinition/condition-code",
                "coding": [
                    {
                        "code": reportable_condition_code,
                        "system": "http://snomed.info/sct",
                    }
                ],
            }:
                stamped_resources.append(resource.get("id"))
                break

    # Finally, check that only and exactly the two expected observations
    # were stamped
    assert len(stamped_resources) == len(expected_stamped_ids)
    for rid in stamped_resources:
        assert rid in expected_stamped_ids
