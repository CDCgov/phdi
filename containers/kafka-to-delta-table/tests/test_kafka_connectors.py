from app.kafka_connectors import connect_to_azure_event_hubs, connect_to_local_kafka
from unittest import mock


# test the connect_to_azure_event_hubs function
# create a mock object for AzureCredentialManager, SparkSession, and StructType
# patch the AzureCredentialManager, from_json, and col functions with the mock object
@mock.patch("app.kafka_connectors.AzureCredentialManager")
@mock.patch("app.kafka_connectors.from_json")
@mock.patch("app.kafka_connectors.col")
def test_connect_to_azure_event_hubs(
    patched_col,
    patched_from_json,
    patched_cred_manager_class):
    # set the return value of the mock object
    cred_manager = mock.Mock()
    cred_manager.get_secret.return_value = "some-secret"
    patched_cred_manager_class.return_value = cred_manager

    # create a mock object for SparkSession and schema setup values
    spark = mock.Mock()
    schema = mock.Mock()

    # setup values for the function parameters
    event_hubs_namespace = "some-event-hubs-namespace"
    event_hub = "some-event-hub"
    connection_string_secret_name = "some-connection-string-secret-name" 
    key_vault_name = "some-key-vault-name"

    # call the function with the mock objects
    result_kafka_data_frame = connect_to_azure_event_hubs(
        spark=spark,
        schema=schema,
        event_hubs_namespace=event_hubs_namespace,
        event_hub=event_hub,
        connection_string_secret_name=connection_string_secret_name,
        key_vault_name=key_vault_name,
    )

    # assert that the mock object's 'get_secret' method was called once with
    # connection_string_name and key_vault_name 
    cred_manager.get_secret.assert_called_once_with(
        secret_name=connection_string_secret_name, key_vault_name=key_vault_name
    )
    # store the connection string secret in a variable
    eh_sasl = f'org.apache.kafka.common.security.plain.PlainLoginModule required username="$ConnectionString" password="{cred_manager.get_secret()}";'

    kafka_server = f"{event_hubs_namespace}.servicebus.windows.net:9093"
    # make sure to use patched from_json and col functions
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
        .select(patched_from_json(patched_col("value").cast("string"), schema).alias("value"))
        .select(patched_col("parsed_value.*"))
    )
    
    # assert that the result of the function call is equal to the expected result
    assert result_kafka_data_frame == kafka_data_frame

# test the connect_to_local_kafka function
# mock the SparkSession and StructType objects
# patch the from_json and col functions with the mock object
@mock.patch("app.kafka_connectors.from_json")
@mock.patch("app.kafka_connectors.col")
def test_connect_to_local_kafka(
    patched_from_json,
    patched_col):
    # setup values for the mock objects for SparkSession and StructType
    spark = mock.Mock()
    schema = mock.Mock()

    # setup values for the function parameters
    kafka_server = "some-kafka-server"
    kafka_topic = "some-kafka-topic"

    # call the function with the mock objects
    result_kafka_data_frame = connect_to_local_kafka(
        spark=spark,
        schema=schema,
        kafka_server=kafka_server,
        kafka_topic=kafka_topic,
    )

    # create the expected result
    kafka_data_frame = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", kafka_server)
        .option("failOnDataLoss", "false")
        .option("subscribe", kafka_topic)
        .option("includeHeaders", "true")
        .load()
        .select(patched_from_json(patched_col("value").cast("string"), schema).alias("value"))
        .select(patched_col("parsed_value.*"))
    )

    # assert that the result of the function call is equal to the expected result
    assert result_kafka_data_frame == kafka_data_frame
