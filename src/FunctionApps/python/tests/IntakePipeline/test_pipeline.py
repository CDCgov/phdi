import json
import pathlib
import pytest
from unittest import mock

from phdi_building_blocks.conversion import convert_batch_messages_to_list

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


@mock.patch("IntakePipeline.standardize_patient_names")
@mock.patch("IntakePipeline.standardize_all_phones")
@mock.patch("IntakePipeline.geocode_patients")
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
    patched_address_standardization,
    patched_phone_standardization,
    patched_name_standardization,
):

    patched_converter.return_value = mock.Mock(
        status_code=200,
        json=lambda: {
            "resourceType": "Bundle",
            "entry": [{"hello": "world"}],
        },
    )

    patched_geocoder = mock.Mock()
    patched_get_geocoder.return_value = patched_geocoder

    patched_standardized_name_data = mock.Mock()
    patched_name_standardization.return_value = patched_standardized_name_data
    patched_standardized_phone_data = mock.Mock()
    patched_phone_standardization.return_value = patched_standardized_phone_data
    patched_standardized_address_data = mock.Mock()
    patched_address_standardization.return_value = patched_standardized_address_data
    patched_linked_id_data = mock.Mock()
    patched_patient_id.return_value = patched_linked_id_data

    patched_upload.return_value = mock.Mock(
        status_code=200,
        json=lambda: {
            "resourceType": "Bundle",
            "entry": [{"resource": {}, "response": {"status": "200 OK"}}],
        },
    )

    patched_access_token = mock.Mock()
    patched_access_token.token = "some-token"
    patched_cred_manager = mock.Mock()
    patched_cred_manager.get_access_token.return_value = patched_access_token

    run_pipeline(
        "MSH|Hello World", MESSAGE_MAPPINGS, "some-fhir-url", patched_cred_manager
    )

    patched_get_geocoder.assert_called_with("smarty-auth-id", "smarty-auth-token")
    patched_converter.assert_called_with(
        message="MSH|Hello World",
        filename="some-filename-1",
        input_data_type=MESSAGE_MAPPINGS["input_data_type"],
        root_template=MESSAGE_MAPPINGS["root_template"],
        template_collection=MESSAGE_MAPPINGS["template_collection"],
        cred_manager=patched_cred_manager,
        fhir_url="some-fhir-url",
    )

    patched_name_standardization.assert_called_with(
        {"resourceType": "Bundle", "entry": [{"hello": "world"}]}
    )
    patched_phone_standardization.assert_called_with(patched_standardized_name_data)
    patched_address_standardization.assert_called_with(
        patched_standardized_phone_data, patched_geocoder
    )

    patched_patient_id.assert_called_with(
        patched_standardized_address_data, TEST_ENV["HASH_SALT"]
    )
    patched_upload.assert_called_with(
        patched_linked_id_data,
        patched_cred_manager,
        "some-fhir-url",
    )
    patched_store.assert_called_with(
        "some-url",
        "output/valid/path",
        f"{MESSAGE_MAPPINGS['filename']}.fhir",
        MESSAGE_MAPPINGS["bundle_type"],
        message_json=patched_linked_id_data,
    )


@mock.patch("IntakePipeline.standardize_patient_names")
@mock.patch("IntakePipeline.standardize_all_phones")
@mock.patch("IntakePipeline.geocode_patients")
@mock.patch("IntakePipeline.add_patient_identifier")
@mock.patch("IntakePipeline.upload_bundle_to_fhir_server")
@mock.patch("IntakePipeline.store_message_and_response")
@mock.patch("IntakePipeline.get_smartystreets_client")
@mock.patch("IntakePipeline.convert_message_to_fhir")
@mock.patch.dict("os.environ", TEST_ENV)
def test_pipeline_invalid_message(
    patched_converter,
    patched_get_geocoder,
    patched_store_msg_resp,
    patched_upload,
    patched_patient_id,
    patched_address_standardization,
    patched_phone_standardization,
    patched_name_standardization,
):
    patched_converter.return_value = mock.Mock(
        status_code=400,
        json=lambda: {"resourceType": "OperationOutcome", "severity": "error"},
    )

    patched_geocoder = mock.Mock()
    patched_get_geocoder.return_value = patched_geocoder

    patched_cred_manager = mock.Mock()

    run_pipeline(
        "MSH|Hello World", MESSAGE_MAPPINGS, "some-fhir-url", patched_cred_manager
    )

    patched_get_geocoder.assert_called_with("smarty-auth-id", "smarty-auth-token")
    patched_converter.assert_called_with(
        message="MSH|Hello World",
        filename="some-filename-1",
        input_data_type=MESSAGE_MAPPINGS["input_data_type"],
        root_template=MESSAGE_MAPPINGS["root_template"],
        template_collection=MESSAGE_MAPPINGS["template_collection"],
        cred_manager=patched_cred_manager,
        fhir_url="some-fhir-url",
    )
    patched_address_standardization.assert_not_called()
    patched_phone_standardization.assert_not_called()
    patched_name_standardization.assert_not_called()
    patched_patient_id.assert_not_called()
    patched_upload.assert_not_called()
    patched_store_msg_resp.assert_called_with(
        container_url="some-url",
        prefix="output/invalid/path",
        message_filename="some-filename-1.hl7",
        response_filename="some-filename-1.hl7.convert-resp",
        bundle_type=MESSAGE_MAPPINGS["bundle_type"],
        message="MSH|Hello World",
        response=patched_converter.return_value,
    )


@mock.patch("IntakePipeline.standardize_patient_names")
@mock.patch("IntakePipeline.standardize_all_phones")
@mock.patch("IntakePipeline.geocode_patients")
@mock.patch("IntakePipeline.add_patient_identifier")
@mock.patch("IntakePipeline.upload_bundle_to_fhir_server")
@mock.patch("IntakePipeline.store_message_and_response")
@mock.patch("IntakePipeline.store_data")
@mock.patch("IntakePipeline.get_smartystreets_client")
@mock.patch("IntakePipeline.convert_message_to_fhir")
@mock.patch.dict("os.environ", TEST_ENV)
def test_pipeline_partial_invalid_message(
    patched_converter,
    patched_get_geocoder,
    patched_store,
    patched_store_msg_resp,
    patched_upload,
    patched_patient_id,
    patched_address_standardization,
    patched_phone_standardization,
    patched_name_standardization,
    partial_failure_message,
):
    convert_success_response = mock.Mock(
        status_code=200,
        json=lambda: {"resourceType": "Bundle", "entry": [{"hello": "world"}]},
    )
    convert_failure_response = mock.Mock(
        status_code=400,
        text=json.dumps(
            {
                "resourceType": "OperationOutcome",
                "severity": "error",
            }
        ),
    )
    patched_converter.side_effect = [
        convert_success_response,
        convert_success_response,
        convert_failure_response,
        convert_success_response,
        convert_success_response,
    ]

    patched_geocoder = mock.Mock()
    patched_get_geocoder.return_value = patched_geocoder

    patched_standardized_name_data = mock.Mock()
    patched_name_standardization.return_value = patched_standardized_name_data
    patched_standardized_phone_data = mock.Mock()
    patched_phone_standardization.return_value = patched_standardized_phone_data
    patched_standardized_address_data = mock.Mock()
    patched_address_standardization.return_value = patched_standardized_address_data
    patched_linked_id_data = mock.Mock()
    patched_patient_id.return_value = patched_linked_id_data
    upload_response_dict = {
        "resourceType": "Bundle",
        "entry": [{"resource": {"hello": "world"}, "response": {"status": "200 OK"}}],
    }
    patched_upload.return_value = mock.Mock(
        status_code=200,
        json=lambda: upload_response_dict,
    )

    messages = convert_batch_messages_to_list(partial_failure_message)
    message_mappings = {
        "file_suffix": "hl7",
        "bundle_type": "VXU",
        "root_template": "VXU_V04",
        "input_data_type": "Hl7v2",
        "template_collection": "microsofthealth/fhirconverter:default",
    }

    patched_cred_manager = mock.Mock()

    # Message 0
    message_mappings["filename"] = "some-filename-0"
    run_pipeline(messages[0], message_mappings, "some-fhir-url", patched_cred_manager)

    # Message 1
    message_mappings["filename"] = "some-filename-1"
    run_pipeline(messages[1], message_mappings, "some-fhir-url", patched_cred_manager)

    # Message 2
    message_mappings["filename"] = "some-filename-2"
    run_pipeline(messages[2], message_mappings, "some-fhir-url", patched_cred_manager)

    # Message 3
    message_mappings["filename"] = "some-filename-3"
    run_pipeline(messages[3], message_mappings, "some-fhir-url", patched_cred_manager)

    # Message 4
    message_mappings["filename"] = "some-filename-4"
    run_pipeline(messages[4], message_mappings, "some-fhir-url", patched_cred_manager)

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
                cred_manager=patched_cred_manager,
                fhir_url="some-fhir-url",
            ),
            mock.call(
                message=messages[1],
                filename="some-filename-1",
                input_data_type=message_mappings["input_data_type"],
                root_template=message_mappings["root_template"],
                template_collection=message_mappings["template_collection"],
                cred_manager=patched_cred_manager,
                fhir_url="some-fhir-url",
            ),
            mock.call(
                message=messages[2],
                filename="some-filename-2",
                input_data_type=message_mappings["input_data_type"],
                root_template=message_mappings["root_template"],
                template_collection=message_mappings["template_collection"],
                cred_manager=patched_cred_manager,
                fhir_url="some-fhir-url",
            ),
            mock.call(
                message=messages[3],
                filename="some-filename-3",
                input_data_type=message_mappings["input_data_type"],
                root_template=message_mappings["root_template"],
                template_collection=message_mappings["template_collection"],
                cred_manager=patched_cred_manager,
                fhir_url="some-fhir-url",
            ),
            mock.call(
                message=messages[4],
                filename="some-filename-4",
                input_data_type=message_mappings["input_data_type"],
                root_template=message_mappings["root_template"],
                template_collection=message_mappings["template_collection"],
                cred_manager=patched_cred_manager,
                fhir_url="some-fhir-url",
            ),
        ]
    )

    patched_address_standardization.call_count = 4
    patched_phone_standardization.call_count = 4
    patched_name_standardization.call_count = 4
    patched_patient_id.call_count = 4
    patched_upload.call_count = 4

    patched_store.assert_has_calls(
        [
            mock.call(
                "some-url",
                "output/valid/path",
                "some-filename-0.fhir",
                "VXU",
                message_json=patched_linked_id_data,
            ),
            mock.call(
                "some-url",
                "output/valid/path",
                "some-filename-1.fhir",
                "VXU",
                message_json=patched_linked_id_data,
            ),
            mock.call(
                "some-url",
                "output/valid/path",
                "some-filename-3.fhir",
                "VXU",
                message_json=patched_linked_id_data,
            ),
            mock.call(
                "some-url",
                "output/valid/path",
                "some-filename-4.fhir",
                "VXU",
                message_json=patched_linked_id_data,
            ),
        ]
    )

    patched_store_msg_resp.assert_called_with(
        container_url="some-url",
        prefix="output/invalid/path",
        message_filename="some-filename-2.hl7",
        response_filename="some-filename-2.hl7.convert-resp",
        bundle_type="VXU",
        message=messages[2],
        response=convert_failure_response,
    )


@mock.patch("IntakePipeline.standardize_patient_names")
@mock.patch("IntakePipeline.standardize_all_phones")
@mock.patch("IntakePipeline.geocode_patients")
@mock.patch("IntakePipeline.add_patient_identifier")
@mock.patch("IntakePipeline.upload_bundle_to_fhir_server")
@mock.patch("IntakePipeline.store_data")
@mock.patch("IntakePipeline.get_smartystreets_client")
@mock.patch("IntakePipeline.convert_message_to_fhir")
@mock.patch.dict("os.environ", TEST_ENV)
def test_pipeline_partial_failed_upload(
    patched_converter,
    patched_get_geocoder,
    patched_store,
    patched_upload,
    patched_patient_id,
    patched_address_standardization,
    patched_phone_standardization,
    patched_name_standardization,
):

    patched_converter.return_value = mock.Mock(
        status_code=200,
        json=lambda: {
            "resourceType": "Bundle",
            "entry": [{"hello": "world"}],
        },
    )

    patched_geocoder = mock.Mock()
    patched_get_geocoder.return_value = patched_geocoder

    patched_standardized_name_data = mock.Mock()
    patched_name_standardization.return_value = patched_standardized_name_data
    patched_standardized_phone_data = mock.Mock()
    patched_phone_standardization.return_value = patched_standardized_phone_data
    patched_standardized_address_data = mock.Mock()
    patched_address_standardization.return_value = patched_standardized_address_data
    patched_linked_id_data = mock.Mock()
    patched_patient_id.return_value = patched_linked_id_data

    patched_upload.return_value = mock.Mock(
        status_code=200,
        json=lambda: {
            "resourceType": "Bundle",
            "entry": [
                {
                    "resource": {"resourceType": "Patient"},
                    "response": {"status": "200 OK"},
                },
                {
                    "resource": {"resourceType": "Organization"},
                    "response": {"status": "400 Bad Request"},
                },
                {
                    "resource": {"resourceType": "Vaccination"},
                    "response": {"status": "200 OK"},
                },
            ],
        },
    )

    patched_access_token = mock.Mock()
    patched_access_token.token = "some-token"
    patched_cred_manager = mock.Mock()
    patched_cred_manager.get_access_token.return_value = patched_access_token

    run_pipeline(
        "MSH|Hello World", MESSAGE_MAPPINGS, "some-fhir-url", patched_cred_manager
    )

    patched_get_geocoder.assert_called_with("smarty-auth-id", "smarty-auth-token")
    patched_converter.assert_called_with(
        message="MSH|Hello World",
        filename="some-filename-1",
        input_data_type=MESSAGE_MAPPINGS["input_data_type"],
        root_template=MESSAGE_MAPPINGS["root_template"],
        template_collection=MESSAGE_MAPPINGS["template_collection"],
        cred_manager=patched_cred_manager,
        fhir_url="some-fhir-url",
    )

    patched_name_standardization.assert_called_with(
        {"resourceType": "Bundle", "entry": [{"hello": "world"}]}
    )
    patched_phone_standardization.assert_called_with(patched_standardized_name_data)
    patched_address_standardization.assert_called_with(
        patched_standardized_phone_data, patched_geocoder
    )

    patched_patient_id.assert_called_with(
        patched_standardized_address_data, TEST_ENV["HASH_SALT"]
    )
    patched_upload.assert_called_with(
        patched_linked_id_data,
        patched_cred_manager,
        "some-fhir-url",
    )
    patched_store.assert_has_calls(
        [
            # Overall successful upload
            mock.call(
                "some-url",
                "output/valid/path",
                f"{MESSAGE_MAPPINGS['filename']}.fhir",
                MESSAGE_MAPPINGS["bundle_type"],
                message_json=patched_linked_id_data,
            ),
            # Individual unsuccessful entry
            mock.call(
                container_url="some-url",
                prefix="output/invalid/path",
                filename=f"{MESSAGE_MAPPINGS['filename']}.entry-1"
                + f".{MESSAGE_MAPPINGS['file_suffix']}",
                bundle_type=MESSAGE_MAPPINGS["bundle_type"],
                message_json={
                    "entry_index": 1,
                    "entry": {
                        "resource": {"resourceType": "Organization"},
                        "response": {"status": "400 Bad Request"},
                    },
                },
            ),
        ]
    )
