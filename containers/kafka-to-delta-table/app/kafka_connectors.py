from pyspark.sql.types import StructType
from pyspark.sql.functions import from_json, col
from pyspark.sql import SparkSession, DataFrame
from phdi.cloud.azure import AzureCredentialManager
from typing import Literal

KAFKA_PROVIDERS = Literal["local_kafka", "azure_event_hubs"]


def connect_to_azure_event_hubs(
    spark: SparkSession,
    schema: StructType,
    event_hubs_namespace: str,
    event_hub: str,
    connection_string_secret_name: str,
    key_vault_name: str,
) -> DataFrame:
    """
    Given a SparkSession object and a schema (StructType) read JSON data from a hub
    (topic) on Azure Event Hubs via Kafka. Authentication with Azure Event Hubs is done
    using a connection string stored in an Azure Key Vault.

    :param spark: A SparkSession object to use for streaming data from Azure Event Hubs.
    :param schema: A schema describing the JSON values read from the topic.
    :param event_hubs_namespace: The namespace of an Azure Event Hubs resource.
        This is the Kafka analog of a cluster.
    :param event_hub: The name of a specific hub withing the the namespace specified by
        'event_hubs_namespace'. This is the Kafka analog of a topic.
    :param connection_string_secret_name: The name of a secret in an Azure key vault
        storing a connection string for the event hubs namespace.
    :param key_vault_name: The name of of the Azure key vault containing the secret
        indicated by 'connection_string_secret_name'.
    """
    credential_manager = AzureCredentialManager()
    connection_string = credential_manager.get_secret(
        secret_name=connection_string_secret_name, key_vault_name=key_vault_name
    )
    
    eh_sasl = f'org.apache.kafka.common.security.plain.PlainLoginModule required username="$ConnectionString" password="{connection_string}";'

    kafka_server = f"{event_hubs_namespace}.servicebus.windows.net:9093"
    kafka_data_frame = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", kafka_server)
        .option("failOnDataLoss", "false")
        .option("subscribe", event_hub)
        .option("includeHeaders", "true")
        .option("kafka.sasl.mechanism", "PLAIN")
        .option("kafka.security.protocol", "SASL_SSL")
        .option("kafka.sasl.jaas.config", eh_sasl)
        .option("kafka.request.timeout.ms", "60000")
        .option("kafka.session.timeout.ms", "30000")
        .load()
        .select(from_json(col("value").cast("string"), schema).alias("parsed_value"))
        .select(col("parsed_value.*"))
    )
    return kafka_data_frame


def connect_to_local_kafka(
    spark: SparkSession, schema: StructType, kafka_server: str, kafka_topic: str
) -> DataFrame:
    """
    Given a SparkSession object and a schema (StructType) read JSON data from a Kafka
    topic.

    :param spark: A SparkSession object to use for streaming data from Kafka.
    :param schema: A schema describing the JSON values read from the topic.
    :param kafka_server: The URL of a Kafka server including port.
    :param kafka_topic: The name of a Kafka topic.
    """
    kafka_data_frame = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", kafka_server)
        .option("failOnDataLoss", "false")
        .option("subscribe", kafka_topic)
        .option("includeHeaders", "true")
        .load()
        .select(from_json(col("value").cast("string"), schema).alias("parsed_value"))
        .select(col("parsed_value.*"))
    )
    return kafka_data_frame
