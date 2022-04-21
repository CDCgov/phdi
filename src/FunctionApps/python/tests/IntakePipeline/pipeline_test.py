from unittest import mock

from IntakePipeline import run_pipeline


TEST_ENV = {
    "INTAKE_CONTAINER_URL": "some-url",
    "INTAKE_CONTAINER_PREFIX": "some-prefix",
    "VALID_OUTPUT_CONTAINER_PATH": "output/valid/path",
    "INVALID_OUTPUT_CONTAINER_PATH": "output/invalid/path",
    "HASH_SALT": "super-secret-definitely-legit-passphrase",
    "SMARTYSTREETS_AUTH_ID": "smarty-auth-id",
    "SMARTYSTREETS_AUTH_TOKEN": "smarty-auth-token",
    "FHIR_URL": "fhir-url",
}

MESSAGE_MAPPINGS = {
    "bundle_type": "VXU",
    "root_template": "VXU_V04",
    "input_data_type": "Hl7v2",
    "template_collection": "microsofthealth/fhirconverter:default",
    "filename": "some-filename-1",
}


@mock.patch("IntakePipeline.transform_bundle")
@mock.patch("IntakePipeline.add_patient_identifier")
@mock.patch("IntakePipeline.upload_bundle_to_fhir_server")
@mock.patch("IntakePipeline.store_data")
@mock.patch("IntakePipeline.get_smartystreets_client")
@mock.patch("IntakePipeline.convert_message_to_fhir")
@mock.patch.dict("os.environ", TEST_ENV)
def test_pipeline_valid_message(
    patched_converter,
    patched_get_geocoder,
    patched_store,
    patched_upload,
    patched_patient_id,
    patched_transform,
):
    patched_converter.return_value = {"hello": "world"}

    patched_geocoder = mock.Mock()
    patched_get_geocoder.return_value = patched_geocoder

    run_pipeline("MSH|Hello World", MESSAGE_MAPPINGS, "some-fhir-url", "some-token")

    patched_get_geocoder.assert_called_with("smarty-auth-id", "smarty-auth-token")
    patched_converter.assert_called_with(
        message="MSH|Hello World",
        input_data_type=MESSAGE_MAPPINGS["input_data_type"],
        root_template=MESSAGE_MAPPINGS["root_template"],
        template_collection=MESSAGE_MAPPINGS["template_collection"],
        access_token="some-token",
        fhir_url="some-fhir-url",
    )
    patched_transform.assert_called_with(patched_geocoder, {"hello": "world"})
    patched_patient_id.assert_called_with(TEST_ENV["HASH_SALT"], {"hello": "world"})
    patched_upload.assert_called_with({"hello": "world"}, "some-token", "some-fhir-url")
    patched_store.assert_called_with(
        "some-url",
        "output/valid/path",
        f"{MESSAGE_MAPPINGS['filename']}.fhir",
        MESSAGE_MAPPINGS["bundle_type"],
        bundle={"hello": "world"},
    )


@mock.patch("IntakePipeline.transform_bundle")
@mock.patch("IntakePipeline.add_patient_identifier")
@mock.patch("IntakePipeline.upload_bundle_to_fhir_server")
@mock.patch("IntakePipeline.store_data")
@mock.patch("IntakePipeline.get_smartystreets_client")
@mock.patch("IntakePipeline.convert_message_to_fhir")
@mock.patch.dict("os.environ", TEST_ENV)
def test_pipeline_invalid_message(
    patched_converter,
    patched_get_geocoder,
    patched_store,
    patched_upload,
    patched_patient_id,
    patched_transform,
):
    patched_converter.return_value = {}

    patched_geocoder = mock.Mock()
    patched_get_geocoder.return_value = patched_geocoder

    run_pipeline("MSH|Hello World", MESSAGE_MAPPINGS, "some-fhir-url", "some-token")

    patched_get_geocoder.assert_called_with("smarty-auth-id", "smarty-auth-token")
    patched_converter.assert_called_with(
        message="MSH|Hello World",
        input_data_type=MESSAGE_MAPPINGS["input_data_type"],
        root_template=MESSAGE_MAPPINGS["root_template"],
        template_collection=MESSAGE_MAPPINGS["template_collection"],
        access_token="some-token",
        fhir_url="some-fhir-url",
    )
    patched_transform.assert_not_called()
    patched_patient_id.assert_not_called()
    patched_upload.assert_not_called()
    patched_store.assert_called_with(
        "some-url",
        "output/invalid/path",
        f"{MESSAGE_MAPPINGS['filename']}.hl7",
        MESSAGE_MAPPINGS["bundle_type"],
        message="MSH|Hello World",
    )
