from app.kafka_to_delta import get_arguments, main, set_selection_flags
import argparse


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
    
def test_get_arguments_local_kafka_local_storage():

    arguments_list = [
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
        "id:long,name:string",
    ]
    selection_flags = set_selection_flags(arguments_list)
    parsed_arguments = get_arguments(arguments_list, selection_flags)
    _check_arguments(arguments_list, parsed_arguments)

def test_get_arguments_azure_event_hubs_and_adlsgen2():
    
    arguments_list = [
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
        "id:long,name:string", 
    ]
    selection_flags = set_selection_flags(arguments_list)
    parsed_arguments = get_arguments(arguments_list, selection_flags)
    _check_arguments(arguments_list, parsed_arguments)