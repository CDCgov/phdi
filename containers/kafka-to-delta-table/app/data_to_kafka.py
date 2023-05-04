from app.storage_connectors import STORAGE_PROVIDERS
from pyspark.sql import SparkSession
from app.utils import get_spark_schema
import sys
import argparse
import json
from pyspark.sql.functions import to_json, struct
from app.kafka_connectors import KAFKA_PROVIDERS, create_kafka_data_frame


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
        choices=["local_storage"],
        type=str,
        required=True,
        help="The type of storage resource that will be written to",
    )
    parser.add_argument(
        "--kafka_provider",
        choices=["local_kafka"],
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
        "--kafka_topic",
        type=str,
        default="",
        required=selection_flags["local_kafka"],
        help="The name of a Kafka topic to read from.",
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
        kafka_data_frame = create_kafka_data_frame(
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
