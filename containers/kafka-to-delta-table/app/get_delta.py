from pyspark.sql import SparkSession
import argparse
import sys
from app.kafka_connectors import KAFKA_PROVIDERS
from app.storage_connectors import STORAGE_PROVIDERS


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


def get_arguments(arguments: list) -> argparse.Namespace:
    """
    Parses command line arguments.

    :param arguments: A list of command line arguments.
    :param selection_flags: A dictionary containing values indicating which Kafka and
        storage providers are selected.
    :return: An argparse.Namespace object containing the parsed arguments.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--delta_table_name",
        type=str,
        required=True,
        help="The name of the Delta table to write to.",
    )

    return parser.parse_args(arguments)


def main():
    """
    Submit a Spark job to read from a Kafka topic and write to a Delta table according
    to configuration provided by command line arguments.
    """
    arguments_list = sys.argv[1:]
    arguments = get_arguments(arguments_list)

    spark = (
        SparkSession.builder.master("local[*]")
        .appName("kafka-to-delta-table")
        .config("spark.sql.debug.maxToStringFields", "100")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    base_path = "./persistent_storage/kafka/"
    df = spark.read.parquet(base_path + arguments.delta_table_name)
    df.show(10)

    sys.exit()


if __name__ == "__main__":
    main()
