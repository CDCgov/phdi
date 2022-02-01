from dataclasses import dataclass
import os


@dataclass
class DecryptSettings:
    """Settings necessary for decrypting a given message. 
    When run remotely, settings are passed by environment variables in the function app, 
    which in turn reference KeyVault variables as mentioned here: https://docs.microsoft.com/en-us/azure/app-service/app-service-key-vault-references

    When run locally, these consult a local file, local.settings.json.
    This can be copied from the Azure portal via:
        ```func azure functionapp fetch-app-settings pitest-functionapp --output-file local.settings.json
            func settings decrypt
        ```
        to get the values direct from the portal, then edited to set the variables.
    """
    private_key_password = os.getenv("PrivateKeyPassword")
    private_key = os.getenv("PrivateKey")
