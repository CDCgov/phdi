# Function Apps

## Create Process

A Terraform `local.function_apps` [set](../../operations/app/terraform/modules/function_app/apps.tf#L1) determines which function apps [the module creates](../../operations/app/terraform/modules/function_app/apps.tf#L11). A [function app submodule](../../operations/app/terraform/modules/common/function_app/main.tf) consolidates duplicate parameters and resources.

### Example

Create a new Python function app:

  1. Add a new item to the `local.function_apps` set with a unique key:

      ```tf
      locals {
        function_apps = {
          default : { runtime = "python" },
          python : { runtime = "python" },
          java : { runtime = "java" },
          infra : { runtime = "python" },
          <unique_key> : { runtime = "python" },
        }
      }
      ```
  2. If the new unique key is `vanilla`, then the new function app is referenced with the following:
    
      ```tf
      module.pdi_function_app["vanilla"]
      ```
  3. Storage account ACL permissions can be updated by adding the [uuid of the new function app](../../operations/app/terraform/modules/storage/data.tf#L13) to `local.data_ace_access`.
      * See [data-access.md](../security/data-access.md#terraform-acl-management) for additional notes.

## Backend

Function apps store their required configuration files in a [dedicated storage account](../../operations/app/terraform/modules/storage/main.tf#L79). This allows us to grant function apps full access to that storage account, while limiting their access to storage accounts that store sensitive data.

## Ad-hoc Deployment

To help facilitate validation of a function app's configuration, it's possible to deploy functions via terraform.
[This](../../operations/app/terraform/modules/function_app/functions_infra.tf) file will deploy a function to validate storage account access to the `infra` function app.
