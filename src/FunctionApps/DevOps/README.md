# DevOps Functions

## ConfirmStorageAccess

Validate access to storage account using [DefaultAzureCredential](https://docs.microsoft.com/en-us/python/api/overview/azure/identity-readme?view=azure-python#defaultazurecredential). Uses managed identity if in cloud or Azure CLI auth if running locally.

![](https://raw.githubusercontent.com/Azure/azure-sdk-for-python/main/sdk/identity/azure-identity/images/DefaultAzureCredentialAuthenticationFlow.png)

## GetIP

Validate function app is functional by fetching IP address.

## Troubleshooting

1. Make sure you are not running as root:
    * `sudo -u <user> bash`
2. Navigate to function app directory:
    * `/src/FunctionApps/`
3. If `.venv` is missing:
    * `python3 -m venv .venv`
4. If `local.settings.json` is missing:
    * `func init`
5. Make sure interpreter is selected for the relevant function app:
    * `Ctrl+Shift+p` > Python: select interpreter > select function app (workspace) > "Enter interpreter path..."
6. Upgrade virtual env pip: 
    * `.venv/bin/python3 -m pip install --upgrade pip`
7. Install libraries locally: 
    * `.venv/bin/python3 -m pip install azure-functions` or `.venv/bin/python3 -m pip install -r requirements.txt`