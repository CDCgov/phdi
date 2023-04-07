from phdi.containers.base_service import BaseService
from pathlib import Path
import json
from typing import Literal
from pydantic import BaseModel, Field, root_validator
import subprocess
from fastapi import Response, status
from app.kafka_connectors import KAFKA_PROVIDERS
from app.storage_connectors import STORAGE_PROVIDERS
from app.utils import validate_schema, SCHEMA_TYPE_MAP, load_schema

# A map of the required values for all supported kafka and storage providers.
REQUIRED_VALUES_MAP = {
    "kafka_provider": {
        "local_kafka": ["kafka_server", "kafka_topic"],
        "azure_event_hubs": [
            "event_hubs_namespace",
            "event_hub",
            "connection_string_secret_name",
            "key_vault_name",
        ],
    },
    "storage_provider": {
        "local_storage": [],
        "adlsgen2": [
            "storage_account",
            "container",
            "client_id",
            "client_secret_name",
            "tenant_id",
            "key_vault_name",
        ],
    },
}


class KafkaToDeltaTableInput(BaseModel):
    """
    The model for requests to the /kafka-to-delta-table endpoint.
    """

    kafka_provider: KAFKA_PROVIDERS = Field(
        description="The type of kafka cluster to read from."
    )
    storage_provider: STORAGE_PROVIDERS = Field(
        description="The type of storage to write to."
    )
    delta_table_name: str = Field(
        description="The name of the Delta table to write to."
    )
    json_schema: dict = Field(
        description=f"A schema describing the format of messages to read from Kafka. "
        "Should be of the form { 'field_name': 'field_type' }. Field names must be "
        "strings and supported field types include: "
        f"{', '.join(list(SCHEMA_TYPE_MAP.keys()))}. If this is provided, then. "
        "'schema_name' must be empty.",
        default={},
        alias="schema",
    )
    schema_name: str = Field(
        description="The name of a schema that was previously uploaded to the service"
        " describing the format of messages to read from Kafka. If this is provided"
        " then 'schema' must be empty.",
        default="",
    )
    kafka_server: str = Field(
        description="The URL of a Kafka server including port. Required when 'kafka_provider' is 'local'.",
        default="",
    )
    event_hubs_namespace: str = Field(
        description="The name of an Azure Event Hubs namespace Required when 'kafka_provider' is 'azure_event_hubs'.",
        default="",
    )
    kafka_topic: str = Field(
        description="The name of a Kafka topic to read from. Required when 'kafka_provider' is 'local'.",
        default="",
    )
    event_hub: str = Field(
        description="The name of an Azure Event Hub to read from. Required when 'kafka_provider' is 'azure_event_hubs'.",
        default="",
    )
    connection_string_secret_name: str = Field(
        description="The connection string for the Azure Event Hubs namespace. Required when 'kafka_provider' is 'azure_event_hubs'.",
        default="",
    )
    storage_account: str = Field(
        description="The name of an Azure Data Lake Storage Gen2 account. Required when 'storage_provider' is 'azure_data_lake_gen2'.",
        default="",
    )
    container: str = Field(
        description="The name of a container in an Azure Storage account specified by 'storage_account'. Required when 'storage_provider' is 'azure_data_lake_gen2'.",
        default="",
    )
    client_id: str = Field(
        description="The client ID of a service principal with access to the Azure Storage account specified by 'storage_account'. Required when 'storage_provider' is 'azure_data_lake_gen2'.",
        default="",
    )
    client_secret_name: str = Field(
        description="The client secret of a service principal with access to the Azure Storage account specified by 'storage_account'. Required when 'storage_provider' is 'azure_data_lake_gen2'.",
        default="",
    )
    tenant_id: str = Field(
        description="The tenant ID of a service principal with access to the Azure Storage account specified by 'storage_account'. Required when 'storage_provider' is 'azure_data_lake_gen2'.",
        default="",
    )
    key_vault_name: str = Field(
        description="The name of the Azure Key Vault containing the secrets specified by 'client_secret_secret_name' and 'connection_string_secret_name'. Required when 'storage_provider' is 'azure_data_lake_gen2' or 'kafka_provider' is 'azure_event_hubs'.",
        default="",
    )

    @root_validator
    def check_for_required_values(cls, values):
        """
        For a given set of values, check that all required values are present based on
        the values of the kafka_provider and storage_provider fields.
        """
        missing_values = []

        for provider_type in REQUIRED_VALUES_MAP:
            provider = values.get(provider_type)
            required_values = REQUIRED_VALUES_MAP.get(provider_type).get(provider)
            for value in required_values:
                if values.get(value) == "":
                    missing_values.append(value)

            if len(missing_values) > 0:
                raise ValueError(
                    f"When the {provider_type} is '{provider}' then the following values must be specified: {', '.join(missing_values)}"
                )
        return values

    @root_validator
    def prohibit_schema_and_schema_name(cls, values):
        if values.get("json_schema") != {} and values.get("schema_name") != "":
            raise ValueError(
                "Values for both 'schema' and 'schema_name' have been "
                "provided. Only one of these values is permitted."
            )
        return values

    @root_validator
    def require_schema_or_schema_name(cls, values):
        if values.get("json_schema") == {} and values.get("schema_name") == "":
            raise ValueError(
                "Values for neither 'schema' nor 'schema_name' have been "
                "provided. One, but not both, of these values is required."
            )
        return values


class KafkaToDeltaTableOutput(BaseModel):
    """
    The model for responses from the /kafka-to-delta-table endpoint.
    """

    status: Literal["success", "failed"] = Field(description="The status of the job.")
    message: str = Field(description="A message describing the status of the job.")
    spark_log: str = Field(description="The log output from the spark job.")


app = BaseService(
    "kafka-to-delta-table", Path(__file__).parent.parent / "description.md"
).start()


@app.post("/kafka-to-delta-table", status_code=200)
async def kafka_to_delta_table(
    input: KafkaToDeltaTableInput, response: Response
) -> KafkaToDeltaTableOutput:
    """
    Stream JSON data from Kafka to a Delta table.

    :param input: A JSON formatted request body with schema specified by the
        KafkaToDeltaTableInput model.
    :return: A JSON formatted response body with schema specified by the
        KafkaToDeltaTableOutput model.
    """
    response_body = {
        "status": "success",
        "message": "",
        "spark_log": "",
    }

    if input.schema_name != "":
        schema = load_schema(input.schema_name)
    else:
        schema = input.json_schema

    schema_validation_results = validate_schema(schema)

    if not schema_validation_results["valid"]:
        response_body["status"] = "failed"
        response_body["message"] = schema_validation_results["errors"][0]
        response.status_code = status.HTTP_400_BAD_REQUEST
        return response_body

    kafka_to_delta_command = [
        "spark-submit",
        "--packages",
        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.2,org.apache.kafka:kafka-clients:3.4.0,io.delta:delta-core_2.12:2.1.0",
        str(Path(__file__).parent / "kafka_to_delta.py"),
        "--kafka_provider",
        input.kafka_provider,
        "--storage_provider",
        input.storage_provider,
        "--delta_table_name",
        input.delta_table_name,
        "--schema",
        f"'{json.dumps(schema)}'",
    ]

    input = input.dict()
    for provider_type in REQUIRED_VALUES_MAP:
        provider = input[provider_type]
        required_values = REQUIRED_VALUES_MAP.get(provider_type).get(provider)
        for value in required_values:
            kafka_to_delta_command.append(f"--{value}")
            kafka_to_delta_command.append(input[value])

    kafka_to_delta_command = " ".join(kafka_to_delta_command)

    kafka_to_delta_result = subprocess.run(
        kafka_to_delta_command, shell=True, capture_output=True, text=True
    )

    response_body["spark_log"] = kafka_to_delta_result.stdout

    if kafka_to_delta_result.returncode != 0:
        response_body["status"] = "failed"
        response_body["spark_log"] = kafka_to_delta_result.stderr

    return response_body
