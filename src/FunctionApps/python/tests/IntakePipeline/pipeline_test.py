from unittest import mock

from IntakePipeline import run_pipeline

TEST_ENV = {
    "HASH_SALT": "super-secret-definitely-legit-passphrase"
}

@mock.patch("IntakePipeline.read_fhir_bundles")
@mock.patch("IntakePipeline.transform_bundle")
@mock.patch("IntakePipeline.add_patient_identifier")
@mock.patch("IntakePipeline.upload_bundle_to_fhir_server")
@mock.patch.dict("os.environ", TEST_ENV)
def test_basic_pipeline(
    patched_upload, patched_patient_id, patched_transform, patched_fhir_read
):

    patched_fhir_read.return_value = [{"hello": "world"}]
    run_pipeline()

    patched_transform.assert_called_with({"hello": "world"})
    patched_patient_id.assert_called_with(TEST_ENV['HASH_SALT'], {"hello": "world"})
    patched_upload.assert_called_with({"hello": "world"})
