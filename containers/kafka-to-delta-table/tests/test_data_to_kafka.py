from app.data_to_kafka import get_arguments, main, set_selection_flags
import argparse
from unittest import mock
import copy
import json


def test_set_selection_flags():
    arguments = [
        "--kafka_provider",
        "local_kafka",
        "--storage_provider",
        "local_storage",
    ]
    selection_flags = set_selection_flags(arguments)
    assert selection_flags["local_kafka"] is True
    assert selection_flags["azure_event_hubs"] is False
    assert selection_flags["local_storage"] is True
    assert selection_flags["adlsgen2"] is False


def _check_arguments(arguments_list: list, parsed_arguments: argparse.Namespace):
    """
    Helper function to confirm that arguments passed to the 'get_arguments()' function
    are parsed correctly.
    """

    for argument_index in range(0, len(arguments_list), 2):
        argument = arguments_list[argument_index][2:]
        value = arguments_list[argument_index + 1]
        assert parsed_arguments.__getattribute__(argument) == value


def test_get_arguments_missing_arguments():
    arguments = []
    selection_flags = set_selection_flags(arguments)
    try:
        get_arguments(arguments, selection_flags)
        exit_code = 0
    except SystemExit as error:
        exit_code = error.code

    assert exit_code == 2


schema = json.dumps({"id": "integer", "name": "string"})
data = json.dumps({"id": "1", "name": "foo"})
LOCAL_KAFKA_LOCAL_STORAGE_ARGUMENTS = [
    "--kafka_provider",
    "local_kafka",
    "--storage_provider",
    "local_storage",
    "--delta_table_name",
    "my-table",
    "--kafka_server",
    "localhost:9092",
    "--kafka_topic",
    "test-topic",
    "--schema",
    schema,
    "--data",
    data,
]

EVENT_HUBS_ADLSGEN2_ARGUMENTS = [
    "--kafka_provider",
    "azure_event_hubs",
    "--storage_provider",
    "adlsgen2",
    "--delta_table_name",
    "my-table",
    "--event_hubs_namespace",
    "some-namespace",
    "--event_hub",
    "some-hub",
    "--connection_string_secret_name",
    "some-connection-string-secret-name",
    "--storage_account",
    "some-storage-account-name",
    "--container",
    "some-container-name",
    "--client_id",
    "some-client-id",
    "--tenant_id",
    "some-tenant-id",
    "--key_vault_name",
    "some-key-vault",
    "--client_secret_name",
    "some-client-secret_name",
    "--schema",
    schema,
    "--data",
    data,
]


def test_get_arguments_local_kafka_local_storage():
    arguments_list = copy.deepcopy(LOCAL_KAFKA_LOCAL_STORAGE_ARGUMENTS)
    selection_flags = set_selection_flags(arguments_list)
    parsed_arguments = get_arguments(arguments_list, selection_flags)
    _check_arguments(arguments_list, parsed_arguments)


def test_get_arguments_azure_event_hubs_and_adlsgen2():
    arguments_list = copy.deepcopy(EVENT_HUBS_ADLSGEN2_ARGUMENTS)
    selection_flags = set_selection_flags(arguments_list)
    parsed_arguments = get_arguments(arguments_list, selection_flags)
    _check_arguments(arguments_list, parsed_arguments)


@mock.patch("app.data_to_kafka.create_kafka_data_frame")
@mock.patch("app.data_to_kafka.struct")
@mock.patch("app.data_to_kafka.to_json")
@mock.patch("app.data_to_kafka.SparkSession")
@mock.patch("app.data_to_kafka.sys")
def test_main_local_kafka_local_storage(
    patched_sys,
    patched_spark_session,
    patched_to_json,
    patched_struct,
    patched_create_kafka_data_frame,
):
    arguments_list = copy.deepcopy(LOCAL_KAFKA_LOCAL_STORAGE_ARGUMENTS)
    arguments_list = ["data_to_kafka.py"] + arguments_list
    patched_sys.argv = arguments_list
    main()
    patched_create_kafka_data_frame.assert_called_once()
    patched_struct.assert_called_once()
    patched_to_json.assert_called_once()
    patched_spark_session.builder.master.assert_called_once()
    patched_sys.exit.assert_called_once()
