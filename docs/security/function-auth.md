# Function Authentication

## Auth Restrictions

Managed identity authentication is required to connect to the PHI data storage accounts, as [account key/SAS auth has been disabled](data-access.md).

## Function Provisioning

It is important to make sure all the necessary files to test authentication locally are provisioned.

While in VSCode, install the Azure Functions extension and follow either to help lay the appropriate foundation:
 1. Follow the [function provisioning instructions](https://github.com/microsoft/vscode-azurefunctions#create-your-first-serverless-app). 
 2. Enter `CTRL+SHIFT+P` and select `Azure Functions: Create Function...`.
    * The first run will create a new project with an HTTP trigger function. **Run again** to create another function with a different trigger (e.g. Blob trigger).

## Auth Solutions

### Http Trigger

Use DefaultAzureCredential:
 * [Java](https://docs.microsoft.com/en-us/java/api/overview/azure/identity-readme?view=azure-java-stable#authenticating-with-defaultazurecredential)

    ```java
    DefaultAzureCredential defaultCredential = new DefaultAzureCredentialBuilder().build();
    final BlobContainerClientBuilder clientBuilder = new BlobContainerClientBuilder()
            .endpoint(endpoint)
            .containerName(container)
            .credential(defaultCredential);
    BlobContainerClient client = clientBuilder.buildClient();
    ```
 * [Python](https://docs.microsoft.com/en-us/python/api/overview/azure/identity-readme?view=azure-python#authenticate-with-defaultazurecredential)

    ```python
    creds = DefaultAzureCredential()

    container_service_client = ContainerClient.from_container_url(
        container_url=f"{storage_url}/{container}",
        credential=creds,
    )
    ```

### Blob Trigger

1. Requires [Azure function core tools v4](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local#v2), [extension version 5.0.0 or later (Bundle v3.x)](https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference?tabs=blob#configure-an-identity-based-connection) and the following app config/`local.settings.json` [settings](https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference?tabs=blob#common-properties-for-identity-based-connections):

    *
      ```json
      "<CONNECTION_NAME_PREFIX>__blobServiceUri": "<blobServiceUri>"
      "<CONNECTION_NAME_PREFIX>__queueServiceUri": "<queueServiceUri>"
      ```
    If the function app does NOT have the Storage Queue Data Contributor role (just ACL for example), include a connection string to a storage account without blob data to temporarily manage the queue:

    *
      ```json
      "<CONNECTION_NAME_PREFIX>__serviceUri": "<blobServiceUri>"
      "AzureWebJobsStorage": "@Microsoft.KeyVault(SecretUri=https://pidev-app-kv.vault.azure.net/secrets/functionappsa)"
      ```

2. [Local development](https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference?tabs=blob#local-development-with-identity-based-connections) requires RBAC roles [Storage Account Contributor, Storage Blob Data Owner, and Storage Queue Data Contributor](https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference?tabs=blob#connecting-to-host-storage-with-an-identity-preview) (queue is used for [Blob receipts](https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-blob-trigger?tabs=in-process%2Cextensionv5&pivots=programming-language-java#blob-receipts))

3. Local development also requires that your external IP is [granted access](https://portal.azure.com/#@cdc.onmicrosoft.com/resource/subscriptions/7d1e3999-6577-4cd5-b296-f518e5c8e677/resourceGroups/prime-ingestion-dev/providers/Microsoft.Storage/storageAccounts/pidevdatasa/networking) to the storage account.

4. Update extension bundle version in `host.json`:
    ```json
    {
      "version": "2.0",
      "extensionBundle": {
        "id": "Microsoft.Azure.Functions.ExtensionBundle",
        "version": "[3.3.0, 4.0.0)"
      } 
    }
    ```

5. DefaultAzureCredential logic can be replaced with the following IF the function app has the Storage Blob Data Contributor role and is not restricted to just ACL:
[Blob output](https://docs.microsoft.com/en-us/java/api/overview/azure/readme?view=azure-java-stable#outputs)