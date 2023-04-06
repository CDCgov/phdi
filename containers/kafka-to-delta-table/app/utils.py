import json
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    FloatType,
    BooleanType,
    TimestampType,
    DateType,
)
from pathlib import Path

# from icecream import ic


# TODO - turn this function into a method of AzureCredentialManager
def get_secret(secret_name: str, key_vault_name: str) -> str:
    """
    Get the value of a secret from an Azure key vault given the names of the vault and
    secret.

    :param secret_name: The name of the secret whose value should be retrieved from the
        key vault.
    :param key_vault_name: The name of the key vault where the secret is stored.
    :return: The value of the secret specified by secret_name.
    """

    credential = DefaultAzureCredential()
    vault_url = f"https://{key_vault_name}.vault.azure.net"
    secret_client = SecretClient(vault_url=vault_url, credential=credential)
    return secret_client.get_secret(secret_name).value


SCHEMA_TYPE_MAP = {
    "string": StringType(),
    "integer": IntegerType(),
    "float": FloatType(),
    "boolean": BooleanType(),
    "date": DateType(),
    "timestamp": TimestampType(),
}


def get_spark_schema(json_schema: str) -> StructType:
    """
    Get a Spark StructType object from a JSON schema string.

    :param json_schema: A string representation of a Spark schema. Should be of the form
        '{"field1": "type1", "field2": "type2"}'.
    :return: A Spark StructType object.
    """

    schema = StructType()
    json_schema = json.loads(json_schema)
    for field in json_schema:
        schema.add(StructField(field, SCHEMA_TYPE_MAP[json_schema[field]], True))
    return schema


def validate_schema(json_schema: dict) -> dict:
    """
    Validate a JSON schema string.

    :param json_schema: A dictionary representation of a schema. Should be of the form
        {"field1": "type1", "field2": "type2"}.
    :return: A dictionary with 'valid' and 'error' keys. If the schema is valid then the
        value of 'valid' will be True and 'errors will be empty. If the schema is not
        valid then the value of 'valid' will be False and 'errors' will contain all of
        validations errors that were found.
    """

    validation_results = {"valid": True, "errors": []}
    valid_types = list(SCHEMA_TYPE_MAP.keys())
    for field, data_type in json_schema.items():
        if type(field) != str:
            validation_results["valid"] = False
            validation_results["errors"].append(
                f"Invalid field name: {field}. Field names must be strings."
            )

        if data_type not in valid_types:
            validation_results["valid"] = False
            validation_results["errors"].append(
                f"Invalid type for field {field}: {data_type}. "
                f"Valid types are {valid_types}."
            )

    return validation_results


def load_schema(schema_name: str) -> dict:
    """
    Load a schema given its name. Look in the 'custom_schemas/' directory first.
    If no custom schemas match the provided name, check the schemas provided by default
    with this service in the 'default_schemas/' directory.

    :param schema_name: The name of a schema to be loaded.
    :return: A dictionary containing the schema.
    """
    custom_schema_path = Path(__file__).parent / "custom_schemas" / schema_name
    try:
        with open(custom_schema_path, "r") as file:
            extraction_schema = json.load(file)
    except FileNotFoundError:
        try:
            default_schema_path = (
                Path(__file__).parent / "default_schemas" / schema_name
            )
            with open(default_schema_path, "r") as file:
                extraction_schema = json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"A schema with the name '{schema_name}' could not be found."
            )
    return extraction_schema
