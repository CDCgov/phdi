import pathlib
import pytest

from unittest import mock
from IntakePipeline.conversion import convert_batch_messages_to_list

from IntakePipeline import run_pipeline


@pytest.fixture()
def partial_failure_message():
    return open(
        pathlib.Path(__file__).parent / "assets" / "batchFileMultipleMessagesOneBad.hl7"
    ).read()


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
    "file_suffix": "hl7",
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
        filename="some-filename-1",
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
        filename="some-filename-1",
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


@mock.patch("IntakePipeline.transform_bundle")
@mock.patch("IntakePipeline.add_patient_identifier")
@mock.patch("IntakePipeline.upload_bundle_to_fhir_server")
@mock.patch("IntakePipeline.store_data")
@mock.patch("IntakePipeline.get_smartystreets_client")
@mock.patch("IntakePipeline.convert_message_to_fhir")
@mock.patch.dict("os.environ", TEST_ENV)
def test_pipeline_partial_invalid_message(
    patched_converter,
    patched_get_geocoder,
    patched_store,
    patched_upload,
    patched_patient_id,
    patched_transform,
    partial_failure_message,
):
    patched_converter.side_effect = [
        {"hello": "world"},
        {"hello": "world"},
        {},
        {"hello": "world"},
        {"hello": "world"},
    ]

    patched_geocoder = mock.Mock()
    patched_get_geocoder.return_value = patched_geocoder

    messages = convert_batch_messages_to_list(partial_failure_message)

    message_mappings = {
        "file_suffix": "hl7",
        "bundle_type": "VXU",
        "root_template": "VXU_V04",
        "input_data_type": "Hl7v2",
        "template_collection": "microsofthealth/fhirconverter:default",
    }

    # Message 0
    message_mappings["filename"] = "some-filename-0"
    run_pipeline(messages[0], message_mappings, "some-fhir-url", "some-token")

    # Message 1
    message_mappings["filename"] = "some-filename-1"
    run_pipeline(messages[1], message_mappings, "some-fhir-url", "some-token")

    # Message 2
    message_mappings["filename"] = "some-filename-2"
    run_pipeline(messages[2], message_mappings, "some-fhir-url", "some-token")

    # Message 3
    message_mappings["filename"] = "some-filename-3"
    run_pipeline(messages[3], message_mappings, "some-fhir-url", "some-token")

    # Message 4
    message_mappings["filename"] = "some-filename-4"
    run_pipeline(messages[4], message_mappings, "some-fhir-url", "some-token")

    # Geocoder called 4 times
    patched_get_geocoder.call_count = 4

    patched_converter.assert_has_calls(
        [
            mock.call(
                message=messages[0],
                filename="some-filename-0",
                input_data_type=message_mappings["input_data_type"],
                root_template=message_mappings["root_template"],
                template_collection=message_mappings["template_collection"],
                access_token="some-token",
                fhir_url="some-fhir-url",
            ),
            mock.call(
                message=messages[1],
                filename="some-filename-1",
                input_data_type=message_mappings["input_data_type"],
                root_template=message_mappings["root_template"],
                template_collection=message_mappings["template_collection"],
                access_token="some-token",
                fhir_url="some-fhir-url",
            ),
            mock.call(
                message=messages[2],
                filename="some-filename-2",
                input_data_type=message_mappings["input_data_type"],
                root_template=message_mappings["root_template"],
                template_collection=message_mappings["template_collection"],
                access_token="some-token",
                fhir_url="some-fhir-url",
            ),
            mock.call(
                message=messages[3],
                filename="some-filename-3",
                input_data_type=message_mappings["input_data_type"],
                root_template=message_mappings["root_template"],
                template_collection=message_mappings["template_collection"],
                access_token="some-token",
                fhir_url="some-fhir-url",
            ),
            mock.call(
                message=messages[4],
                filename="some-filename-4",
                input_data_type=message_mappings["input_data_type"],
                root_template=message_mappings["root_template"],
                template_collection=message_mappings["template_collection"],
                access_token="some-token",
                fhir_url="some-fhir-url",
            ),
        ]
    )

    patched_transform.call_count = 4
    patched_patient_id.call_count = 4
    patched_upload.call_count = 4
    patched_store.assert_has_calls(
        [
            mock.call(
                "some-url",
                "output/valid/path",
                "some-filename-0.fhir",
                "VXU",
                bundle={"hello": "world"},
            ),
            mock.call(
                "some-url",
                "output/valid/path",
                "some-filename-1.fhir",
                "VXU",
                bundle={"hello": "world"},
            ),
            mock.call(
                "some-url",
                "output/invalid/path",
                "some-filename-2.hl7",
                "VXU",
                message=messages[2],
            ),
            mock.call(
                "some-url",
                "output/valid/path",
                "some-filename-3.fhir",
                "VXU",
                bundle={"hello": "world"},
            ),
            mock.call(
                "some-url",
                "output/valid/path",
                "some-filename-4.fhir",
                "VXU",
                bundle={"hello": "world"},
            ),
        ]
    )
