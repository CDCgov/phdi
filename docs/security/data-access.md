# Data Access

Access keys to the [PHI storage account](https://portal.azure.com/#@cdc.onmicrosoft.com/resource/subscriptions/7d1e3999-6577-4cd5-b296-f518e5c8e677/resourceGroups/prime-ingestion-test/providers/Microsoft.Storage/storageAccounts/pitestdatasa/overview) have been disabled and [ACL](https://docs.microsoft.com/en-us/azure/storage/blobs/data-lake-storage-access-control) permissions are in its place.
Members of AD group [CT-PRIMEIngestion-AZ-Owners](https://portal.azure.com/#blade/Microsoft_AAD_IAM/GroupDetailsMenuBlade/Members/groupId/0fd85c9a-0da3-4d00-b123-f44ef16469e7) already have full access, but any resources and/or service principals will need to be granted access (managed by Terraform).

## Terraform ACL Management

Storage account containers and directories are managed by Terraform with ACL permissions applied via the following:

`operations/app/terraform/modules/storage/data.tf`:
```sh
locals {
  data_containers = ["bronze", "bronze-additional-records", "fhir-exports", "silver", "gold"]
  data_ace_access = [
    { permissions = "---", id = null, type = "other", scope = "access" },
    { permissions = "---", id = null, type = "other", scope = "default" },
    { permissions = "r-x", id = null, type = "group", scope = "access" },
    { permissions = "r-x", id = null, type = "group", scope = "default" },
    { permissions = "rwx", id = null, type = "user", scope = "access" },
    { permissions = "rwx", id = null, type = "user", scope = "default" },
    { permissions = "rwx", id = null, type = "mask", scope = "access" },
    { permissions = "rwx", id = null, type = "mask", scope = "default" },
    { permissions = "rwx", id = var.adf_uuid, type = "user", scope = "access" },
    { permissions = "rwx", id = var.adf_uuid, type = "user", scope = "default" },
    { permissions = "rwx", id = var.pdi_function_app_uuid, type = "user", scope = "access" },
    { permissions = "rwx", id = var.pdi_function_app_uuid, type = "user", scope = "default" },
    { permissions = "r-x", id = var.infrastructure_function_app_uuid, type = "user", scope = "access" }
  ]
}
```

**NOTE**: While setting `default` permissions updates new files, ACL propagation is required to update existing files. The easist way to do this is by right clicking the storage account in the [Azure Storage Explorer](https://azure.microsoft.com/en-us/features/storage-explorer/).

## Access Demo
* [DefaultAzureCredential](https://docs.microsoft.com/en-us/python/api/overview/azure/identity-readme?view=azure-python#defaultazurecredential). Uses managed identity if in cloud or Azure CLI auth if running locally.

  ![](https://raw.githubusercontent.com/Azure/azure-sdk-for-python/main/sdk/identity/azure-identity/images/DefaultAzureCredentialAuthenticationFlow.png)

* Working [python function example](https://portal.azure.com/#blade/WebsitesExtension/FunctionMenuBlade/code/resourceId/%2Fsubscriptions%2F7d1e3999-6577-4cd5-b296-f518e5c8e677%2FresourceGroups%2Fprime-ingestion-test%2Fproviders%2FMicrosoft.Web%2Fsites%2Fpitest-infra-functionapp%2Ffunctions%2FConfirmStorageAccess):
  * Passing in query parameter `container=bronze` validates if access exists *(via function app managed identity)*