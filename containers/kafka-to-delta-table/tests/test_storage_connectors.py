from app.storage_connectors import connect_to_adlsgen2
from pyspark.sql import SparkSession
from unittest import mock


@mock.patch("app.storage_connectors.AzureCredentialManager")
def test_connect_to_adlsgen2(patched_cred_manager_class):
    cred_manager = mock.Mock()
    cred_manager.get_secret.return_value = "some-secret"
    patched_cred_manager_class.return_value = cred_manager

    spark = mock.Mock()

    storage_account = "some-storage-account"
    container = "some-container"
    tenant_id = "some-tenant-id"
    client_id = "some-client-id"
    client_secret_name = "some-client-secret-name"
    key_vault_name = "some-key-vault-name"

    spark, base_path = connect_to_adlsgen2(
        spark=spark,
        storage_account=storage_account,
        container=container,
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret_name=client_secret_name,
        key_vault_name=key_vault_name,
    )
    cred_manager.get_secret.assert_called_once_with(
        secret_name=client_secret_name, key_vault_name=key_vault_name
    )
    conf_set_calls = [
        mock.call(
            f"fs.azure.account.auth.type.{storage_account}.dfs.core.windows.net",
            "OAuth",
        ),
        mock.call(
            f"fs.azure.account.oauth.provider.type.{storage_account}.dfs.core.windows.net",
            "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
        ),
        mock.call(
            f"fs.azure.account.oauth2.client.id.{storage_account}.dfs.core.windows.net",
            client_id,
        ),
        mock.call(
            f"fs.azure.account.oauth2.client.secret.{storage_account}.dfs.core.windows.net",
            cred_manager.get_secret(),
        ),
        mock.call(
            f"fs.azure.account.oauth2.client.endpoint.{storage_account}.dfs.core.windows.net",
            f"https://login.microsoftonline.com/{tenant_id}/oauth2/token",
        ),
        mock.call("fs.azure.createRemoteFileSystemDuringInitialization", "false"),
    ]

    spark.conf.set.assert_has_calls(conf_set_calls)
    assert len(conf_set_calls) == spark.conf.set.call_count
    assert (
        base_path
        == f"abfss://{container}@{storage_account}.dfs.core.windows.net/kafka/"
    )
