from pyspark.sql import SparkSession
from typing import Literal
from phdi.cloud.azure import AzureCredentialManager


STORAGE_PROVIDERS = Literal["local_storage", "adlsgen2"]


def connect_to_adlsgen2(
    spark: SparkSession,
    storage_account: str,
    container: str,
    tenant_id: str,
    client_id: str,
    client_secret_name: str,
    key_vault_name: str,
) -> tuple[SparkSession, str, bool]:
    """
    Add required configuration to a SparkSession object to allow it to connect to Azure
    Data Lake gen 2 (ADLS gen2) storage. Connection to ADLS gen2 requires an Azure App
    Registration with read and write access to an azure stroage account specified by
    'storage_account_name'. A secret, with name corresponding to 'client_secret_name',
    for this app registration must be stored in an Azure Key Vault with name specified
    by 'key_vault_name'.

    :param spark: A SparkSession object that configuration for connecting to ADLS gen2
        should be added to.
    :param storage_account: The name of an ADLS gen2 storage account to connect to.
    :param container: The name of a container within the storage accound specified by
        'storage_account' that should be connected to.
    :param tenant_id: The tenant id of the Azure tenant associate with the storage
        account.
    :param client_id: The id of the app aegistration being used for authorization.
    :param client_secret_name: The name of secret in an Azure Key Vault for the app
        registration.
    :param key_vault_name: The name of the Azure key vault where the secret is stored.
    """
    credential_manager = AzureCredentialManager()
    client_secret = credential_manager.get_secret(
        secret_name=client_secret_name, key_vault_name=key_vault_name
    )
    spark.conf.set(
        f"fs.azure.account.auth.type.{storage_account}.dfs.core.windows.net",
        "OAuth",
    )
    spark.conf.set(
        f"fs.azure.account.oauth.provider.type.{storage_account}.dfs.core.windows.net",
        "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
    )
    spark.conf.set(
        f"fs.azure.account.oauth2.client.id.{storage_account}.dfs.core.windows.net",
        client_id,
    )
    spark.conf.set(
        f"fs.azure.account.oauth2.client.secret.{storage_account}.dfs.core.windows.net",
        client_secret,
    )
    spark.conf.set(
        f"fs.azure.account.oauth2.client.endpoint.{storage_account}.dfs.core.windows.net",  # noqa
        f"https://login.microsoftonline.com/{tenant_id}/oauth2/token",
    )
    spark.conf.set("fs.azure.createRemoteFileSystemDuringInitialization", "false")

    base_path = f"abfss://{container}@{storage_account}.dfs.core.windows.net/kafka/"
    offset = Something(base_path)
    return spark, base_path, offset
