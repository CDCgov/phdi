from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential


# TODO - turn this function into a method of AzureCredentialManager
def get_secret(secret_name: str, key_vault_name: str) -> str:
    """
    Get the value of a secret from an Azure key vault given the names of the vault and
    secret.

    :param secret_name: The name of the secret whose value should be retreived from the
        key vault.
    :param key_vault_name: The name of the key vault where the secret is stored.
    :return: The value of the secret specified by secret_name.
    """

    credential = DefaultAzureCredential()
    vault_url = f"https://{key_vault_name}.vault.azure.net"
    secret_client = SecretClient(vault_url=vault_url, credential=credential)
    return secret_client.get_secret(secret_name).value
