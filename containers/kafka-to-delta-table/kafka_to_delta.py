from app.storage_connectors import connect_to_adlsgen2
from app.kafka_connectors import connect_to_azure_event_hubs, connect_to_local_kafka
from pyspark.sql import SparkSession
import argparse
import sys
from app.utils import get_spark_schema
from app.kafka_connectors import KAFKA_PROVIDERS
from app.storage_connectors import STORAGE_PROVIDERS
from icecream import ic


def set_selection_flags(arguments: list) -> dict:
    """
    Sets the value of the selection_flags dictionary to True if the corresponding
    command line argument is present in the list of arguments.

    :param arguments: A list of command line arguments.
    :return: A dictionary containing values indicating which Kafka and storage providers
        are selected.
    """
    selection_flags = {}
    providers = KAFKA_PROVIDERS.__args__ + STORAGE_PROVIDERS.__args__
    for flag in providers:
        if flag in arguments:
            selection_flags[flag] = True
        else:
            selection_flags[flag] = False

    return selection_flags


def get_arguments(arguments: list, selection_flags: dict) -> argparse.Namespace:
    """
    Parses command line arguments.

    :param arguments: A list of command line arguments.
    :param selection_flags: A dictionary containing values indicating which Kafka and
        storage providers are selected.
    :return: An argparse.Namespace object containing the parsed arguments.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--storage_provider",
        choices=["local_storage", "adlsgen2"],
        type=str,
        required=True,
        help="The type of storage resource that will be written to",
    )
    parser.add_argument(
        "--kafka_provider",
        choices=["local_kafka", "azure_event_hubs"],
        type=str,
        required=True,
        help="The type of kafka cluster to read from.",
    )
    parser.add_argument(
        "--kafka_server",
        type=str,
        required=selection_flags["local_kafka"],
        help="The URL of a Kafka server including port.",
    )
    parser.add_argument(
        "--event_hubs_namespace",
        type=str,
        required=selection_flags["azure_event_hubs"],
        help="The name of an Azure Event Hubs namespace.",
    )
    parser.add_argument(
        "--kafka_topic",
        type=str,
        default="",
        required=selection_flags["local_kafka"],
        help="The name of a Kafka topic to read from.",
    )
    parser.add_argument(
        "--event_hub",
        type=str,
        default="",
        required=selection_flags["azure_event_hubs"],
        help="The name of an Azure Event Hub to read from.",
    )
    parser.add_argument(
        "--connection_string_secret_name",
        type=str,
        required=selection_flags["azure_event_hubs"],
        help="The connection string for the Azure Event Hubs namespace.",
    )
    parser.add_argument(
        "--storage_account",
        type=str,
        required=selection_flags["adlsgen2"],
        help="The name of an Azure Data Lake Storage Gen2 account.",
    )
    parser.add_argument(
        "--container",
        type=str,
        required=selection_flags["adlsgen2"],
        help="The name of a container in an Azure Storage account specified by "
        "'--storage_account'.",
    )
    parser.add_argument(
        "--delta_table_name",
        type=str,
        required=True,
        help="The name of the Delta table to write to.",
    )
    parser.add_argument(
        "--client_id",
        type=str,
        required=selection_flags["adlsgen2"],
        help="The client ID of a service principal with access to the Azure Storage "
        "account specified by '--storage_account'.",
    )
    parser.add_argument(
        "--tenant_id",
        type=str,
        required=selection_flags["adlsgen2"],
        help="The tenant ID of the service principal specified by '--client_id' with "
        "access to the Azure Storage account specified by '--storage_account'.",
    )
    parser.add_argument(
        "--key_vault_name",
        type=str,
        required=(selection_flags["adlsgen2"] or selection_flags["azure_event_hubs"]),
        help="The name of an Azure Key Vault containing all required secrets for "
        "connection to all Azure storage and Kafka resources.",
    )
    parser.add_argument(
        "--client_secret_name",
        type=str,
        required=selection_flags["adlsgen2"],
        help="The name of the secret in the Azure Key Vault specified by "
        "'--key_vault_name' containing the client secret of the service principal "
        "specified by '--client_id'.",
    )
    parser.add_argument(
        "--schema",
        type=str,
        required=True,
        help="The schema of the data to be written to the Delta table as a JSON string "
        "with the form '{'field1': 'type1', 'field2': 'type2'}'.",
    )

    return parser.parse_args(arguments)


def main():
    """
    Submit a Spark job to read from a Kafka topic and write to a Delta table according
    to configuration provided by command line arguments.
    """
    ic("hello from kafka")
    arguments_list = sys.argv[1:]
    selection_flags = set_selection_flags(arguments_list)
    arguments = get_arguments(arguments_list, selection_flags)

    kafka_topic_mappings = {
        "azure_event_hubs": arguments.event_hub,
        "local_kafka": arguments.kafka_topic,
    }

    spark = (
        SparkSession.builder.master("local[*]")
        .appName("kafka-to-delta-table")
        .config("spark.sql.debug.maxToStringFields", "100")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    base_path = "./persistent_storage/kafka/"

    if selection_flags["adlsgen2"]:
        spark, base_path = connect_to_adlsgen2(
            spark,
            arguments.storage_account,
            arguments.container,
            arguments.tenant_id,
            arguments.client_id,
            arguments.client_secret_name,
            arguments.key_vault_name,
        )

    schema = get_spark_schema(arguments.schema)
    if selection_flags["azure_event_hubs"]:
        kafka_data_frame = connect_to_azure_event_hubs(
            spark,
            schema,
            arguments.event_hubs_namespace,
            arguments.event_hub,
            arguments.connection_string_secret_name,
            arguments.key_vault_name,
        )

    elif selection_flags["local_kafka"]:
        kafka_data_frame = connect_to_local_kafka(
            spark, schema, arguments.kafka_server, arguments.kafka_topic
        )

    delta_table_path = (
        base_path + f"{kafka_topic_mappings[arguments.kafka_provider]}-table"
    )
    checkpoint_path = (
        base_path + f"{kafka_topic_mappings[arguments.kafka_provider]}-checkpoint"
    )

    query = (
        kafka_data_frame.writeStream.option("checkpointLocation", checkpoint_path)
        .outputMode("append")
        .format("delta")
        .trigger(availableNow=True)
        .start(delta_table_path)
    )

    query.awaitTermination(10)
    sys.exit()


if __name__ == "__main__":
    main()
