from unittest import mock

from IntakePipeline import run_pipeline


TEST_ENV = {
    "INTAKE_CONTAINER_URL": "some-url",
    "INTAKE_CONTAINER_PREFIX": "some-prefix",
    "OUTPUT_CONTAINER_PATH": "output/path",
    "HASH_SALT": "super-secret-definitely-legit-passphrase",
    "SMARTYSTREETS_AUTH_ID": "smarty-auth-id",
    "SMARTYSTREETS_AUTH_TOKEN": "smarty-auth-token",
    "FHIR_URL": "fhir-url",
}


@mock.patch("IntakePipeline.read_fhir_bundles")
@mock.patch("IntakePipeline.transform_bundle")
@mock.patch("IntakePipeline.add_patient_identifier")
@mock.patch("IntakePipeline.upload_bundle_to_fhir_server")
@mock.patch("IntakePipeline.store_bundle")
@mock.patch("IntakePipeline.get_fhirserver_cred_manager")
@mock.patch("IntakePipeline.get_smartystreets_client")
@mock.patch.dict("os.environ", TEST_ENV)
def test_basic_pipeline(
    patched_get_geocoder,
    patched_get_fhirserver_cred_manager,
    patched_store,
    patched_upload,
    patched_patient_id,
    patched_transform,
    patched_fhir_read,
):

    patched_geocoder = mock.Mock()
    patched_get_geocoder.return_value = patched_geocoder

    patched_fhirserver_cred_manager = mock.Mock()
    patched_get_fhirserver_cred_manager.return_value = patched_fhirserver_cred_manager

    patched_fhir_read.return_value = [{"hello": "world"}]
    run_pipeline()

    patched_get_geocoder.assert_called_with("smarty-auth-id", "smarty-auth-token")
    patched_fhir_read.assert_called_with("some-url", "some-prefix")
    patched_transform.assert_called_with(patched_geocoder, {"hello": "world"})
    patched_patient_id.assert_called_with(TEST_ENV["HASH_SALT"], {"hello": "world"})
    patched_upload.assert_called_with(
        patched_fhirserver_cred_manager, {"hello": "world"}
    )
    patched_store.assert_called_with("some-url", "output/path", {"hello": "world"})
