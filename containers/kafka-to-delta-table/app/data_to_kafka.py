from storage_connectors import STORAGE_PROVIDERS
from pyspark.sql.types import StructType
from pyspark.sql import SparkSession, DataFrame
from utils import get_spark_schema
import sys
import argparse
import json
from pyspark.sql.functions import to_json, struct
from kafka_connectors import KAFKA_PROVIDERS


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
    parser.add_argument(
        "--data",
        type=str,
        required=True,
        help="The data to be written to the kafka table as a JSON string.",
    )

    return parser.parse_args(arguments)


def connect_to_local_kafka(
    spark: SparkSession,
    schema: StructType,
    data: list[dict],
) -> DataFrame:
    """
    Given a SparkSession object and a schema (StructType) read JSON data from a Kafka
    topic.

    :param spark: A SparkSession object to use for streaming data from Kafka.
    :param schema: A schema describing the JSON values read from the topic.
    :param data: A list of the data to be written
    """
    kafka_data_frame = spark.createDataFrame(data, schema)
    return kafka_data_frame


def main():
    """
    Upload data to kafka instance
    """
    arguments_list = sys.argv[1:]
    selection_flags = set_selection_flags(arguments_list)
    arguments = get_arguments(arguments_list, selection_flags)

    spark = (
        SparkSession.builder.master("local[*]")
        .appName("kafka-to-delta-table")
        .config("spark.sql.debug.maxToStringFields", "100")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ALL")

    schema = get_spark_schema(arguments.schema)

    if selection_flags["local_kafka"]:
        kafka_data_frame = connect_to_local_kafka(
            spark,
            schema,
            data=json.loads(arguments.data),
        )

    df_json = kafka_data_frame.select(to_json(struct("*")).alias("value"))

    (
        df_json.write.format("kafka")
        .option("kafka.bootstrap.servers", arguments.kafka_server)
        .option("topic", arguments.kafka_topic)
        .save()
    )

    sys.exit()


if __name__ == "__main__":
    main()
