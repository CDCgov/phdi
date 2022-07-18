module "pdi_function_app" {
  for_each = local.function_apps
  source   = "../common/function_app"

  primary = {
    name                       = replace("${var.resource_prefix}-${each.key}-functionapp", "-default-", "-")
    location                   = var.location
    resource_group_name        = var.resource_group_name
    app_service_plan_id        = var.app_service_plan
    storage_account_name       = var.sa_functionapps.name
    storage_account_access_key = var.sa_functionapps.primary_access_key
    environment                = var.environment
    subnet_id                  = var.cdc_app_subnet_id
    application_key_vault_id   = var.application_key_vault_id
    version                    = each.value.version
    always_on                  = each.value.always_on
  }

  app_settings = {
    WEBSITE_DNS_SERVER = "168.63.129.16"

    # App Insights
    PRIVATE_KEY                            = "@Microsoft.KeyVault(SecretUri=https://${var.resource_prefix}-app-kv.vault.azure.net/secrets/PrivateKey)"
    PRIVATE_KEY_PASSWORD                   = "@Microsoft.KeyVault(SecretUri=https://${var.resource_prefix}-app-kv.vault.azure.net/secrets/PrivateKeyPassword)"
    AZURE_STORAGE_CONTAINER_NAME           = "bronze"
    APPINSIGHTS_INSTRUMENTATIONKEY         = var.ai_instrumentation_key
    APPLICATIONINSIGHTS_CONNECTION_STRING  = var.ai_connection_string
    BUILD_FLAGS                            = "UseExpressBuild"
    FUNCTIONS_WORKER_RUNTIME               = each.value.runtime
    SCM_DO_BUILD_DURING_DEPLOYMENT         = each.value.SCM_DO_BUILD_DURING_DEPLOYMENT
    VDHSFTPHostname                        = "vdhsftp.vdh.virginia.gov"
    VDHSFTPPassword                        = "@Microsoft.KeyVault(SecretUri=https://${var.resource_prefix}-app-kv.vault.azure.net/secrets/VDHSFTPPassword)"
    VDHSFTPUsername                        = "USDS_CDC"
    XDG_CACHE_HOME                         = "/tmp/.cache"
    WEBSITE_RUN_FROM_PACKAGE               = each.value.WEBSITE_RUN_FROM_PACKAGE
    DATA_STORAGE_ACCOUNT                   = var.sa_data_name
    ENABLE_ORYX_BUILD                      = each.value.ENABLE_ORYX_BUILD
    "${each.value.mi_blobServiceName}"     = each.value.mi_blobServiceUri
    "${each.value.mi_queueServiceName}"    = each.value.mi_queueServiceUri
    "${each.value.mi_accountName}"         = each.value.mi_accountValue
    fhir_url                               = each.value.fhir_url
    "AzureWebJobs.convertToFhir.Disabled"  = each.value.AzureWebJobs_convertToFhir_Disabled
    SMARTYSTREETS_AUTH_ID                  = "@Microsoft.KeyVault(SecretUri=https://${var.resource_prefix}-app-kv.vault.azure.net/secrets/SmartyStreetsAuthID)"
    SMARTYSTREETS_AUTH_TOKEN               = "@Microsoft.KeyVault(SecretUri=https://${var.resource_prefix}-app-kv.vault.azure.net/secrets/SmartyStreetsAuthToken)"
    CONTAINER_URL                          = "https://${var.resource_prefix}datasa${var.environment == "skylight" ? "1" : ""}.blob.core.windows.net/bronze"
    INTAKE_CONTAINER_URL                   = "https://${var.resource_prefix}datasa${var.environment == "skylight" ? "1" : ""}.blob.core.windows.net/bronze"
    INTAKE_CONTAINER_PREFIX                = "decrypted/valid-messages/"
    OUTPUT_CONTAINER_PATH                  = "processed"
    CSV_INPUT_PREFIX                       = each.value.CSV_INPUT_PREFIX
    CSV_OUTPUT_PREFIX                      = each.value.CSV_OUTPUT_PREFIX
    HASH_SALT                              = "@Microsoft.KeyVault(SecretUri=https://${var.resource_prefix}-app-kv.vault.azure.net/secrets/salt)"
    FHIR_URL                               = "https://${var.resource_prefix}-fhir.azurehealthcareapis.com"
    "AzureWebJobs.IntakePipeline.Disabled" = each.value.AzureWebJobs_IntakePipeline_Disabled
    AzureWebJobsStorage__accountName       = each.value.AzureWebJobsStorage__accountName
    AzureWebJobsStorage__blobServiceUri    = each.value.AzureWebJobsStorage__blobServiceUri
    AzureWebJobsStorage__queueServiceUri   = each.value.AzureWebJobsStorage__queueServiceUri
    AzureWebJobsStorage__tableServiceUri   = each.value.AzureWebJobsStorage__tableServiceUri
    INVALID_OUTPUT_CONTAINER_PATH          = each.value.INVALID_OUTPUT_CONTAINER_PATH
    VALID_OUTPUT_CONTAINER_PATH            = each.value.VALID_OUTPUT_CONTAINER_PATH

  }
}
